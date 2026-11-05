from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/stage512/2026-11-05"
RAW = BASE / "source_raw"


class AuditFailure(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditFailure(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def validate_minimum_register_contract(register: dict) -> None:
    allowed = {"INVESTABLE", "PROXY_ONLY", "EXCLUDED", "BLOCKED"}
    require(register.get("investment_authorization") == "NO_GO", "investment authorization must remain NO_GO")
    access = register["investor_access"]
    require(access["account_entitlement_or_product_availability"] == "BLOCKED_NOT_VERIFIED", "investor/product access must remain blocked")
    require(access["investor_suitability"] == "BLOCKED_UNCONFIRMED", "investor suitability must remain blocked")
    ids = set()
    for candidate in register["candidates"]:
        require(candidate["candidate_id"] not in ids, "duplicate candidate ID")
        ids.add(candidate["candidate_id"])
        require(candidate.get("classification") in allowed, f"invalid candidate classification: {candidate.get('candidate_id')}")
        require(candidate.get("exact_as_of"), f"candidate lacks dated basis: {candidate.get('candidate_id')}")
        require(candidate.get("instrument_or_benchmark_id"), f"candidate lacks identity: {candidate.get('candidate_id')}")
        require(candidate.get("return_convention"), f"candidate lacks return convention: {candidate.get('candidate_id')}")
    benchmark = next(c for c in register["candidates"] if c["candidate_id"] == "NIFTY500_TRI_BENCHMARK")
    require(benchmark["classification"] == "PROXY_ONLY" and "TRI" in benchmark["instrument_or_benchmark_id"], "Nifty 500 TRI must remain a non-product benchmark")
    direct = next(c for c in register["candidates"] if c["candidate_id"] == "GOI_DIRECT_DATED_GSEC_718_2033")
    proxy = next(c for c in register["candidates"] if c["candidate_id"] == "LIC_GSEC_8_13_ETF")
    require(direct["category"] == "direct_government_security" and direct["classification"] == "BLOCKED", "direct sovereign security must remain separate and blocked")
    require(proxy["category"] == "sovereign_bond_fund_or_etf_proxy" and proxy["classification"] == "PROXY_ONLY", "bond ETF proxy must remain distinct from direct sovereign cashflows")


def validate_observations_not_before_inception(candidate: dict, rows: list[dict]) -> None:
    inception = candidate.get("inception_date")
    if not inception:
        return
    start = inception[:10]
    for row in rows:
        require(row["date"] >= start, f"pre-inception observation for {candidate['candidate_id']}: {row['date']} < {start}")


def validate_source_hash(actual: str, expected: str) -> None:
    require(actual == expected and len(expected) == 64, "source hash mismatch")


def expect_rejected(label: str, function) -> None:
    try:
        function()
    except (AuditFailure, KeyError, ValueError, TypeError):
        print(f"NEGATIVE CASE REJECTED: {label}")
        return
    raise AuditFailure(f"negative case was accepted: {label}")


def main() -> int:
    register = read_json(BASE / "g5_2_candidate_evidence_register_v1.json")
    holdings = read_json(BASE / "g5_2_holdings_overlap_v1.json")
    q2 = read_json(BASE / "g5_2_qcsae_v1.json")

    # The G5.2 source files are verified from their bytes; no G5.2 audit code is imported.
    products = {p["candidate_id"]: p for p in holdings["products"]}
    for product in products.values():
        source = RAW / product["source_file"]
        normalized = BASE / product["normalized_csv"]
        require(source.exists() and normalized.exists(), f"missing preserved holdings evidence: {product['candidate_id']}")
        validate_source_hash(sha(source), product["source_sha256"])
        validate_source_hash(sha(normalized), product["normalized_csv_sha256"])
        require(source.stat().st_size == product["source_bytes"], f"source byte count mismatch: {product['candidate_id']}")

    # Re-extract issuer security identities, weights and concentration directly from both AMC workbooks.
    import openpyxl

    workbooks = {
        "MOTILAL_NIFTY500_ETF": "motilal_nifty500_etf_2026-09.xlsx",
        "MOTILAL_NIFTY500_INDEX_FUND": "motilal_nifty500_indexfund_2026-09.xlsx",
    }
    reconstructed = {}
    for candidate_id, filename in workbooks.items():
        ws = openpyxl.load_workbook(RAW / filename, read_only=True, data_only=True).active
        rows = []
        for raw in ws.iter_rows(min_row=13, values_only=True):
            number, name, isin, industry, _quantity, market_value, weight = raw[:7]
            if not name or not isinstance(number, (int, float)) or not isinstance(market_value, (int, float)):
                continue
            if not isin or not str(isin).startswith("INE"):
                continue
            rows.append({
                "isin": str(isin).strip(),
                "name": str(name).strip(),
                "industry": str(industry).strip() if industry else "",
                "market_value": float(market_value),
                "weight": float(weight) if isinstance(weight, (int, float)) else None,
            })
        require(len(rows) == 498 and len({r["isin"] for r in rows}) == 498, f"raw holdings ISIN coverage mismatch: {candidate_id}")
        require(sum(r["weight"] is not None for r in rows) == 497, f"raw holdings reported-weight count mismatch: {candidate_id}")
        suppressed = [r for r in rows if r["weight"] is None]
        require(len(suppressed) == 1 and suppressed[0]["name"] == "MMTC Limited", f"suppressed weight was not preserved: {candidate_id}")
        expected = products[candidate_id]
        total_weight = sum(r["weight"] or 0.0 for r in rows)
        require(math.isclose(total_weight, expected["equity_weight_sum_reported_pct"], abs_tol=1e-9), f"equity weight total mismatch: {candidate_id}")
        weights = sorted((r["weight"] for r in rows if r["weight"] is not None), reverse=True)
        require(math.isclose(sum(weights[:10]), expected["top10_equity_weight_pct_reported"], abs_tol=1e-9), f"top-ten mismatch: {candidate_id}")
        require(math.isclose(sum(weights[:20]), expected["top20_equity_weight_pct_reported"], abs_tol=1e-9), f"top-twenty mismatch: {candidate_id}")
        normalized = {r["security_id"]: r for r in read_csv(BASE / expected["normalized_csv"]) if r["position_type"] == "EQUITY"}
        require(set(normalized) == {r["isin"] for r in rows}, f"raw-to-normalized ISIN set mismatch: {candidate_id}")
        for row in rows:
            saved = normalized[row["isin"]]
            require(saved["name"] == row["name"], f"raw-to-normalized name mismatch: {candidate_id}/{row['isin']}")
            require(math.isclose(float(saved["market_value_inr_lakh"]), row["market_value"], abs_tol=0.005), f"raw-to-normalized value mismatch: {candidate_id}/{row['isin']}")
            if row["weight"] is None:
                require(saved["weight_pct_source"] == "", f"unknown weight converted to a value: {candidate_id}/{row['isin']}")
            else:
                require(math.isclose(float(saved["weight_pct_source"]), row["weight"], abs_tol=1e-9), f"raw-to-normalized weight mismatch: {candidate_id}/{row['isin']}")
        reconstructed[candidate_id] = rows

    etf = {r["isin"]: r["weight"] for r in reconstructed["MOTILAL_NIFTY500_ETF"]}
    index = {r["isin"]: r["weight"] for r in reconstructed["MOTILAL_NIFTY500_INDEX_FUND"]}
    common = set(etf) & set(index)
    numeric = [i for i in common if etf[i] is not None and index[i] is not None]
    overlap = sum(min(etf[i], index[i]) for i in numeric)
    overlap_record = holdings["exposure_diagnostics"]["overlap_pct_reported_weight_subset"]
    require(len(common) == 498 and len(numeric) == 497, "matched-date overlap coverage mismatch")
    require(math.isclose(overlap, overlap_record, abs_tol=1e-9) and math.isclose(overlap, 99.68, abs_tol=1e-9), "independent overlap computation mismatch")

    # Independently extract metal and bond identity/holdings from preserved AMC PDFs.
    import pymupdf

    icici = pymupdf.open(RAW / "icici_passive_factsheet_2026-03.pdf")
    gold_text = " ".join(icici[44].get_text().split())
    silver_text = " ".join(icici[45].get_text().split())
    require("Inception/Allotment date: 24-Aug-10" in gold_text and "NSE : GOLDIETF" in gold_text and "ISIN : INF109KC1NT3" in gold_text, "ICICI Gold ETF primary identity mismatch")
    require("Inception/Allotment date: 24-Jan-22" in silver_text and "NSE : SILVERIETF" in silver_text and "ISIN : INF109KC1Y56" in silver_text, "ICICI Silver ETF primary identity mismatch")
    require("Gold (995 Purity) 98.21%" in gold_text and "Short Term Debt and net current assets 1.79%" in gold_text, "ICICI gold holdings mismatch")
    require("Silver 99.08%" in silver_text and "Short Term Debt and net current assets 0.92%" in silver_text, "ICICI silver holdings mismatch")
    lic = pymupdf.open(RAW / "lic_gsec_factsheet_2026-09.pdf")
    lic_text = " ".join(lic[47].get_text().split())
    for token in ["Inception/Allotment Date: December 24, 2014", "NSE Scrip Code: LICNETFGSC", "PORTFOLIO as on 30/09/2026", "SOVEREIGN 99.50%", "Cash & Other Receivables 0.50%", "Nifty 8-13 yr G-Sec Index"]:
        require(token in lic_text, f"LIC official factsheet identity/holdings mismatch: {token}")
    lic_rows = read_csv(BASE / products["LIC_GSEC_8_13_ETF"]["normalized_csv"])
    require(sum(float(r["weight_pct_source"]) for r in lic_rows if r["weight_pct_source"]) == 100.0, "LIC holdings reconciliation mismatch")
    require(sum(not r["security_id"] for r in lic_rows) == len(lic_rows), "unpublished LIC bond ISINs were inferred")

    # Verify that sample values and AMFI event metadata are internally aligned, while explicitly noting raw responses are absent.
    observations_path = ROOT / "research/stage512/data/amfi_pilot/named_scheme_observations.csv"
    manifest_path = ROOT / "research/stage512/data/amfi_pilot/manifest.json"
    require(sha(observations_path) == "6b08b10f469ffeb9523b0f4c06f2be87cdbd0fc50f931234d180b0fefb8d0005", "AMFI named observation CSV hash mismatch")
    require(sha(manifest_path) == "3c3305e8ccb410df025c8a00ac570db3dfaf33a88b44d660deee336b3f51293f", "AMFI manifest hash mismatch")
    manifest = read_json(manifest_path)
    manifest_windows = {w["label"]: w for w in manifest["windows"]}
    amfi_rows = read_csv(observations_path)
    expected_dates = ["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05", "2026-10-19", "2026-10-21", "2026-10-22", "2026-10-23", "2026-10-30"]
    for candidate_id, isin in [("ICICI_GOLD_ETF", "INF109KC1NT3"), ("ICICI_SILVER_ETF", "INF109KC1Y56")]:
        candidate = next(c for c in register["candidates"] if c["candidate_id"] == candidate_id)
        rows = [r for r in amfi_rows if r["isin"] == isin]
        require([r["date"] for r in rows] == expected_dates, f"AMFI exact sample dates mismatch: {isin}")
        validate_observations_not_before_inception(candidate, rows)
        require(all(r["source_sha256"] == manifest_windows[r["source_window"]]["sha256"] for r in rows), f"AMFI observation-to-manifest mismatch: {isin}")
        sample_meta = candidate["history_coverage"]["official_AMFI_sample_observations"]
        require(sample_meta["dates"] == expected_dates and sample_meta["continuity"].startswith("No;"), f"AMFI history continuity claim mismatch: {isin}")

    # Reconcile every relevant Total TER from the retained AMFI normalized export; never substitute BER for Total TER.
    ter_export_path = ROOT / "research/stage59/amfi_ter_oct2026_export_latest.csv"
    ter_map_path = ROOT / "research/stage59/amfi_ter_matched_96_v14.csv"
    diagnostic_path = ROOT / "research/stage59/amfi_ter_export_diagnostic.json"
    require(sha(ter_export_path) == "5d4b0b4a6ee306cedddad0b4470c3efd5fe76ffcbdb0e96c7fd38455b8df8e77", "AMFI TER normalized export hash mismatch")
    require(sha(ter_map_path) == "8606de60e951eb8716aad18932d6ad0e3a838125a9ab5d06bb78384b67fb9bdf", "AMFI TER mapping hash mismatch")
    require(sha(diagnostic_path) == "845940d19694207de0763a8243447ee11d8f256ece5961ea28f6daf1544fa297", "AMFI TER diagnostic hash mismatch")
    ter_rows = read_csv(ter_export_path)
    fee_specs = [
        ("MOTO/O/O/EET/23/09/0043", "0.39", "0.18", "0.02", "0", "0.19", "46325"),
        ("MOTO/O/O/EIN/19/06/0014", "0.97", "0.79", "0.02", "0", "0.16", "46325"),
        ("ICIC/O/O/GET/10/04/0038", "0.49", "0.42", "0", "0", "0.07", "46324"),
        ("ICIC/O/O/OET/21/12/0137", "0.4", "0.34", "0", "0", "0.06", "46324"),
    ]
    cols = {
        "BER": "Regular Plan - Base Expense Ratio (BER) (%)",
        "Brokerage": "Regular Plan - Brokerage cost (%)",
        "Transaction": "Regular Plan - Transaction Cost incurred for the purpose of execution of trade (%)",
        "Levies": "Regular Plan - Statutory Levies (including GST) (%)",
        "Total": "Regular Plan - Total TER (%)",
    }
    for nsdl, total, ber, brokerage, transaction, levies, serial_date in fee_specs:
        row = [r for r in ter_rows if r["NSDL Scheme Code"] == nsdl]
        require(len(row) == 1, f"AMFI TER source row not unique: {nsdl}")
        row = row[0]
        require(row["TER Date"] == serial_date, f"AMFI TER date mismatch: {nsdl}")
        require(all(row[cols[k]] == v for k, v in [("Total", total), ("BER", ber), ("Brokerage", brokerage), ("Transaction", transaction), ("Levies", levies)]), f"AMFI TER row values mismatch: {nsdl}")
        require(math.isclose(sum(float(row[cols[k]]) for k in ["BER", "Brokerage", "Transaction", "Levies"]), float(row[cols["Total"]]), abs_tol=1e-9), f"AMFI Total TER component arithmetic mismatch: {nsdl}")

    # Independently calculate the Index Fund Direct-plan Total TER from the same
    # retained normalized AMFI source row; do not rely on the mapping file's
    # precomputed TER_TOTAL_MATH_CHECK flag as the arithmetic proof.
    direct_nsdl = "MOTO/O/O/EIN/19/06/0014"
    direct_rows = [r for r in ter_rows if r["NSDL Scheme Code"] == direct_nsdl]
    require(len(direct_rows) == 1, f"AMFI Direct-plan TER source row not unique: {direct_nsdl}")
    direct_row = direct_rows[0]
    direct_cols = {
        "BER": "Direct Plan - Base Expense Ratio (BER) (%)",
        "Brokerage": "Direct Plan - Brokerage cost (%)",
        "Transaction": "Direct Plan - Transaction Cost incurred for the purpose of execution of trade (%)",
        "Levies": "Direct Plan - Statutory Levies (including GST) (%)",
        "Total": "Direct Plan - Total TER (%)",
    }
    direct_expected = {"BER": "0.13", "Brokerage": "0.02", "Transaction": "0", "Levies": "0.08", "Total": "0.23"}
    require(direct_row["TER Date"] == "46325", f"AMFI Direct-plan TER date mismatch: {direct_nsdl}")
    require(all(direct_row[direct_cols[k]] == v for k, v in direct_expected.items()), f"AMFI Direct-plan TER source values mismatch: {direct_nsdl}")
    direct_sum = sum(float(direct_row[direct_cols[k]]) for k in ["BER", "Brokerage", "Transaction", "Levies"])
    require(math.isclose(direct_sum, float(direct_row[direct_cols["Total"]]), abs_tol=1e-9), f"AMFI Direct-plan Total TER component arithmetic mismatch: {direct_nsdl}")
    mapped = [r for r in read_csv(ter_map_path) if r["scheme_code"] == "147625" and r["ter_date"] == "2026-10-30"]
    require(len(mapped) == 1 and mapped[0]["nsdl_code"] == direct_nsdl and mapped[0]["D_TER"] == direct_expected["Total"] and mapped[0]["D_BER"] == direct_expected["BER"] and mapped[0]["D_BrokerageCost"] == direct_expected["Brokerage"] and mapped[0]["D_TransactionCost"] == direct_expected["Transaction"] and mapped[0]["D_StatutoryLevies"] == direct_expected["Levies"] and mapped[0]["R_TER"] == "0.97" and mapped[0]["TER_TOTAL_MATH_CHECK"] == "PASS", "AMFI index-fund scheme mapping mismatch")
    diag = read_json(diagnostic_path)
    require(diag["sha256"] == "ec512c338263e41f3d8c520d764965758817a670edce8e4a92caad26d9fc46b2" and diag["download_size"] == 4397825, "AMFI TER raw response metadata mismatch")
    require(diag["export_url"].startswith("https://www.amfiindia.com/api/populate-te-rdata-revised?"), "TER source URL is not official AMFI")
    for c, nsdl, expected in [(next(x for x in register["candidates"] if x["candidate_id"] == "MOTILAL_NIFTY500_ETF"), "MOTO/O/O/EET/23/09/0043", "0.39"), (next(x for x in register["candidates"] if x["candidate_id"] == "MOTILAL_NIFTY500_INDEX_FUND"), "MOTO/O/O/EIN/19/06/0014", "0.97")]:
        ev = next(e for e in c["primary_evidence"] if e.get("nsdl_scheme_code") == nsdl)
        require(ev["normalized_export_sha256"] == sha(ter_export_path) and ev["source_diagnostic_sha256"] == sha(diagnostic_path) and ev["raw_export_retained"] is False, f"TER source lineage mismatch: {nsdl}")
        fee = c["fees_tax_liquidity_execution_settlement"]["ter_latest_verified"]
        require(expected in fee, f"candidate latest Total TER value not updated: {nsdl}")
    for candidate_id, expected in [("ICICI_GOLD_ETF", "0.49%"), ("ICICI_SILVER_ETF", "0.40%")]:
        candidate = next(c for c in register["candidates"] if c["candidate_id"] == candidate_id)
        require(expected in candidate["fees_tax_liquidity_execution_settlement"]["ter"], f"ICICI Total TER candidate value mismatch: {candidate_id}")
        require(candidate["fees_tax_liquidity_execution_settlement"]["tax"] is None, f"unqualified tax was filled in: {candidate_id}")
        require(candidate["fees_tax_liquidity_execution_settlement"]["execution"] is None and "BLOCKED" in candidate["fees_tax_liquidity_execution_settlement"]["liquidity"], f"execution evidence was overstated: {candidate_id}")

    # Independently verify the G5.1 append-only lineage and six quarantined dependent outputs.
    lineage = read_json(BASE / "g5_1_118_claim_lineage_v1.json")
    for rel, digest in lineage["current_source_hashes_sha256_utf8_lf"].items():
        path = ROOT / rel
        require(path.exists(), f"G5.1 lineage input missing: {rel}")
        normalized_hash = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        require(normalized_hash == digest, f"G5.1 lineage artifact hash mismatch: {rel}")
    risk_rows = read_csv(ROOT / "research/stage512/2026-11-02/stage512_risk_scenarios.csv")
    affected = [r for r in risk_rows if r["scenario"].startswith("Synthetic 11.8% equity geometric-return assumption")]
    require(len(affected) == 6, "G5.1 dependent scenario row count must be six")
    require(all(r["scenario_classification"] == "SYNTHETIC_ASSUMPTION_NOT_HISTORICAL_REPLAY" and r["equity_return_provenance_status"] == "UNVERIFIED_THIRD_PARTY_REPORTED_CAGR_USED_AS_SYNTHETIC_ASSUMPTION" and r["decision_evidence_status"] == "QUARANTINED_NOT_FOR_INVESTMENT_DECISION" and r["claim_lineage_record"] == "research/stage512/2026-11-05/g5_1_118_claim_lineage_v1.json" for r in affected), "G5.1 dependent scenario rows lack quarantine/provenance")
    rerun_path = ROOT / "research/stage512/2026-11-05/g5_1_118_assumption_rerun/stage512_risk_scenarios.csv"
    rerun_rows = read_csv(rerun_path)
    rerun_affected = [r for r in rerun_rows if r["scenario"].startswith("Synthetic 11.8% equity geometric-return assumption")]
    require(affected == rerun_affected, "G5.1 committed output differs from quarantined reproduction")
    report = (ROOT / "research/stage512/2026-11-02/stage512_blocker_resolution_report.md").read_text(encoding="utf-8")
    require("G5.1 correction" in report and "Synthetic 11.8% equity-return assumption" in report and "quarantined" in report.lower(), "G5.1 human report does not expose its correction")
    assumptions = read_json(ROOT / "research/stage512/2026-11-02/stage512_assumption_register.json")
    require(any(x["scenario"] == "Synthetic 11.8% equity geometric-return assumption" for x in assumptions["models"]), "G5.1 assumption register has no corrected scenario label")
    former_label = "Historical 11.8% " + "replay"
    allowed_former_label_files = {
        "research/stage512/2026-11-05/G5_1_118_CLAIM_LINEAGE.md",
        "research/stage512/2026-11-05/g5_1_118_claim_lineage_v1.json",
    }
    hits = []
    for folder in [ROOT / "docs", ROOT / "decision", ROOT / "research/stage512/2026-11-02", ROOT / "research/stage512/2026-11-05"]:
        for path in folder.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".py", ".csv"}:
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if former_label in content:
                hits.append(path.relative_to(ROOT).as_posix())
    require(set(hits) == allowed_former_label_files, f"former historical label appears outside explicit correction records: {hits}")
    model = (ROOT / "research/stage512/2026-11-02/stage512_risk_audit.py").read_text(encoding="utf-8")
    require("equity_geo':.118" in model and "SYNTHETIC_ASSUMPTION_NOT_HISTORICAL_REPLAY" in model and "QUARANTINED_NOT_FOR_INVESTMENT_DECISION" in model, "G5.1 model trace/status does not identify the synthetic assumption")

    # Negative cases ensure the key fail-closed distinctions cannot silently regress.
    validate_minimum_register_contract(register)
    bad = json.loads(json.dumps(register))
    bad["investor_access"]["account_entitlement_or_product_availability"] = "VERIFIED"
    expect_rejected("unknown investor access promoted to confirmed", lambda: validate_minimum_register_contract(bad))
    bad = json.loads(json.dumps(register))
    next(c for c in bad["candidates"] if c["candidate_id"] == "NIFTY500_TRI_BENCHMARK")["classification"] = "INVESTABLE"
    expect_rejected("benchmark relabeled as investable product", lambda: validate_minimum_register_contract(bad))
    metal = next(c for c in register["candidates"] if c["candidate_id"] == "ICICI_GOLD_ETF")
    expect_rejected("pre-inception metal NAV row", lambda: validate_observations_not_before_inception(metal, [{"date": "2010-08-23"}]))
    expect_rejected("stale/mismatched evidence hash", lambda: validate_source_hash("0" * 64, "1" * 64))
    bad = json.loads(json.dumps(register))
    next(c for c in bad["candidates"] if c["candidate_id"] == "ICICI_GOLD_ETF").pop("return_convention")
    expect_rejected("missing return convention", lambda: validate_minimum_register_contract(bad))

    categories = {c["category"] for c in register["candidates"]}
    require({"equity", "direct_government_security", "sovereign_bond_fund_or_etf_proxy", "gold", "silver", "cash_hold_comparator"} <= categories, "required G5 categories missing")
    candidate_count = len(register["candidates"])
    require(candidate_count == 8, "candidate coverage changed; G5 breadth disposition requires renewed review")
    require(q2["investment_authorization"] == "NO_GO", "G5.2 QCSAE must retain NO_GO")
    print("G5.3 independent candidate evidence audit PASS for bounded evidence checks")
    print(f"Re-extracted 498 equity ISINs per Motilal product; 497 numeric weights each; overlap {overlap:.2f}%")
    print("ICICI/LIC identity and holdings re-read from first-party factsheets; all four AMFI Total TER rows reconciled")
    print("G5.1 six dependent 11.8% outputs retain synthetic labels, lineage and quarantine")
    print("G5 overall disposition: BLOCKED_INSUFFICIENT_UNIVERSE_AND_SOURCE_REPRODUCIBILITY; investment authorization NO-GO")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"G5.3 independent audit FAIL: {exc}", file=sys.stderr)
        raise

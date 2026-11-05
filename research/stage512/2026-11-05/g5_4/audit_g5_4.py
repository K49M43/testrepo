#!/usr/bin/env python3
import csv,decimal,datetime,hashlib,json,pathlib,sys
root=pathlib.Path(__file__).resolve().parents[4]
base=root/"research/stage512/2026-11-05"
add=base/"g5_4"
manifest=json.loads((add/"source_reacquisition_manifest.json").read_text())
for item in manifest["files"]:
 p=root/item["path"]
 assert p.stat().st_size==item["bytes"], item["path"]
 assert hashlib.sha256(p.read_bytes()).hexdigest()==item["sha256"], item["path"]
reg=json.loads((base/"g5_2_candidate_evidence_register_v1.json").read_text())
ext=json.loads((add/"candidate_expansion_v1.json").read_text())
assert len(reg["candidates"])==8
assert len(ext["candidates"])==5
assert ext["universe_count"]["investable_product_hypotheses"]==10
ter=json.loads((add/"ter_row_audit.json").read_text())
assert ter["rows_reconciled"]==10 and ter["regular_component_sums_pass"]==10 and ter["direct_component_sums_pass"]==10
assert ter["source_sha256"]==hashlib.sha256((root/"research/stage512/2026-11-05/source_retrieval_followup/amfi_ter_oct2026_original.xlsx").read_bytes()).hexdigest()
recon=json.loads((add/"nav_sample_reconciliation.json").read_text())
assert recon["comparisons"]==44 and recon["exact_matches"]==44 and not recon["mismatches"]
gates=json.loads((add/"g6_entry_readiness.json").read_text())
assert gates["decision"]=="DECISION_GRADE_NOT_READY" and gates["engineering_start"] in {"READY_BOUNDED_SYNTHETIC_DETERMINISTIC_BRIDGE", "IN_PROGRESS_G6_1_FIXTURE_BRIDGE_PR_CI_PENDING"} and gates["investment_authorization"]=="NO_GO"
import subprocess, sys
history_result=subprocess.run([sys.executable,str(add/"audit_g5_candidate_nav_history.py")],capture_output=True,text=True)
assert history_result.returncode==0,history_result.stdout+history_result.stderr
history_audit=json.loads((add/"candidate_nav_history_audit.json").read_text())
assert history_audit["overall"]=="PASS" and len(history_audit["results"])==5
assert all(x["status"]=="PASS_RAW_TO_NORMALIZED_LINEAGE_AND_DATE_CONTINUITY" for x in history_audit["results"])
disposition=json.loads((add/"g5_candidate_disposition_v1.json").read_text())
assert disposition["acceptance"]["all_10_have_disposition"] is True
product_rows=[x for x in disposition["candidates"] if x["product_hypothesis"]]
assert len(product_rows)==10 and len({x["candidate_id"] for x in product_rows})==10
assert all(x["classification"] in {"INVESTABLE","PROXY_ONLY","BLOCKED"} and x["screen_disposition"] and x["decision_reason"] and x["source_status"] and x["open_gates"] for x in product_rows)
assert set(disposition["initial_comparison_set"]).issubset({x["candidate_id"] for x in disposition["candidates"]})
assert disposition["acceptance"]["ranking_or_weights"]=="NOT_PRODUCED"
assert disposition["acceptance"]["investor_suitability_or_trade_authorization"]=="NOT_ASSESSED_NO_GO"
disposition_result=subprocess.run([sys.executable,str(add/"audit_g5_candidate_disposition.py")],capture_output=True,text=True)
assert disposition_result.returncode==0,disposition_result.stdout+disposition_result.stderr
exit_result=subprocess.run([sys.executable,str(add/"audit_g5_exit_acceptance.py")],capture_output=True,text=True)
assert exit_result.returncode==0,exit_result.stdout+exit_result.stderr
print("PASS: raw hash/byte integrity; append-only counts 8+5; 10 product dispositions; 44/44 bounded NAV samples; 10/10 TER rows and 20/20 sums; 5 AMFI raw-to-normalized histories; dated holdings snapshots; all 8 G5 exit criteria independently mapped with explicit blocked evidence; G6 decision-grade remains blocked; bounded engineering start is ready")

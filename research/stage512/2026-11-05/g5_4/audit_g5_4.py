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
assert gates["decision"]=="DECISION_GRADE_NOT_READY" and gates["engineering_start"]=="READY_BOUNDED_SYNTHETIC_DETERMINISTIC_BRIDGE" and gates["investment_authorization"]=="NO_GO"
import subprocess, sys
history_result=subprocess.run([sys.executable,str(add/"audit_g5_candidate_nav_history.py")],capture_output=True,text=True)
assert history_result.returncode==0,history_result.stdout+history_result.stderr
history_audit=json.loads((add/"candidate_nav_history_audit.json").read_text())
assert history_audit["overall"]=="PASS" and len(history_audit["results"])==4
assert all(x["status"]=="PASS_RAW_TO_NORMALIZED_LINEAGE_AND_DATE_CONTINUITY" for x in history_audit["results"])
print("PASS: raw hash/byte integrity; append-only counts 8+5; 10 product hypotheses; 44/44 bounded NAV samples; 10/10 TER rows and 20/20 sums; 4 AMFI raw-to-normalized histories and strict monthly joins; G6 decision-grade remains blocked; bounded engineering start is ready")

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
recon=json.loads((add/"nav_sample_reconciliation.json").read_text())
assert recon["comparisons"]==44 and recon["exact_matches"]==44 and not recon["mismatches"]
gates=json.loads((add/"g6_entry_readiness.json").read_text())
assert gates["decision"]=="NOT_READY" and gates["investment_authorization"]=="NO_GO"
print("PASS: raw hash/byte integrity; append-only counts 8+5; 10 product hypotheses; 44/44 bounded NAV observations; G6 remains fail-closed")

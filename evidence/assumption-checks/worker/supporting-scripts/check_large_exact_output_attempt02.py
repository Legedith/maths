"""Probe admitted arithmetic whose exact result exceeds Python's decimal limit."""
import json
import traceback
from pathlib import Path
from atlas_checks import check_transfer

root = Path(__file__).resolve().parents[1] / "project"
payload = json.loads((root / "fixtures/assumption-checks/weighted-counterexample.json").read_text(encoding="utf-8"))
payload["id"] = "public-large-exact-result"
payload["graph"] = {"n": 6, "edges": [{"u": 0, "v": v, "conductance": 999999999999} for v in range(1, 6)]}
payload["source"], payload["target"] = 0, 1
payload["assumptions"] = []
payload["provenance"]["kind"] = "synthetic"
payload["provenance"]["source_locator"] = "Public arithmetic representation probe, not a source-derived theorem."

def product(count: int) -> dict:
    if count == 1:
        return {"kind": "quantity", "name": "tree_mass"}
    left = count // 2
    return {"kind": "binary", "op": "mul", "left": product(left), "right": product(count-left)}

payload["claim"] = {"kind": "binary", "op": "lt", "left": {"kind": "rational", "value": 0}, "right": product(140)}
report = {"scope": "Public post-freeze output-size probe; 281 AST nodes, depth below 20, admitted 12-digit weights. The exact positive product is (999999999999)^700.", "input": payload}
try:
    result = check_transfer(payload)
    report.update({"escaped_exception": False, "verdict": result["verdict"], "exact_value_digits": len(result["claim_evaluation"]["trace"]["right"]["value"]), "result": result})
except Exception as exc:
    report.update({"escaped_exception": True, "exception_type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
(root / "evidence/assumption-checks/worker/root-large-output-attempt-02.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k not in ("input", "traceback", "result")}, indent=2))

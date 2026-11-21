"""Audit every run in outputs/: are all quoted lines really in the input scripts, and do the
S1 labels line up with the run they label?  Read-only: it never changes outputs or labels.

python eval/audit_outputs.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from continuity_checker import ingest  # noqa: E402


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def audit_run(run: Path) -> dict:
    rep = json.loads((run / "report.json").read_text(encoding="utf-8"))
    src = Path(rep["meta"]["input"])
    if not src.is_absolute():
        src = ROOT / src
    eps = {e.number: norm(e.text) for e in ingest.load(src)}
    exact = fuzzy_only = 0
    bad = []
    for i in rep["issues"]:
        for side in ("prior", "new"):
            f = i[side]
            if norm(f["quote"]) in eps[f["episode"]]:
                exact += 1
            elif f.get("quote_score", 0) >= 85:
                fuzzy_only += 1
                bad.append(f"{i['id']} {side} Ep{f['episode']}: {f['quote'][:70]!r} (fuzzy {f['quote_score']:.0f})")
            else:
                bad.append(f"{i['id']} {side} Ep{f['episode']}: NOT FOUND {f['quote'][:70]!r}")
    return {"run": str(run.relative_to(ROOT)), "version": rep["meta"].get("prompt_version"), "issues": len(rep["issues"]),
            "quotes_exact": exact, "quotes_fuzzy_only": fuzzy_only, "problems": bad}


def audit_labels() -> list[str]:
    lab = json.loads((ROOT / "eval/S1_labels.json").read_text(encoding="utf-8"))
    rep = json.loads((ROOT / lab["run"] / "report.json").read_text(encoding="utf-8"))
    issues = rep["issues"]
    msgs = [f"labels file points at {lab['run']} ({len(issues)} issues); {len(lab['labels'])} labels"]
    for l in lab["labels"]:
        i = issues[l["n"] - 1] if l["n"] <= len(issues) else None
        if i is None or i["id"] != l["id"]:
            msgs.append(f"MISMATCH n={l['n']} label id {l['id']} vs report id {i and i['id']}")
        elif [i["prior"]["episode"], i["new"]["episode"]] != l["episodes"] or i["issue_type"] != l["type"] or i["severity"] != l["severity"]:
            msgs.append(f"FIELD MISMATCH n={l['n']} {l['id']}")
    ids = [l["id"] for l in lab["labels"]]
    if len(set(ids)) != len(ids):
        msgs.append("duplicate ids in labels")
    # does the later re-render of the same series contain the same flags?
    for other in sorted((ROOT / "outputs").glob("S1_generated_*")):
        if other.name != Path(lab["run"]).name:
            o = json.loads((other / "report.json").read_text(encoding="utf-8"))["issues"]
            same = {i["id"] for i in o} == set(ids)
            msgs.append(f"{other.name}: {len(o)} issues, same issue ids as labelled run: {same}")
    return msgs


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    runs = sorted(p.parent for p in (ROOT / "outputs").rglob("report.json"))
    print("| Run | Prompt version | Flags | Quotes verbatim | Quotes fuzzy-only |\n|---|---|---|---|---|")
    problems = []
    for r in runs:
        a = audit_run(r)
        print(f"| {a['run']} | {a['version']} | {a['issues']} | {a['quotes_exact']} | {a['quotes_fuzzy_only']} |")
        problems += [f"{a['run']}: {p}" for p in a["problems"]]
    print("\nQuote problems:" if problems else "\nQuote problems: none")
    for p in problems:
        print(" -", p)
    print("\nS1 label consistency:")
    for m in audit_labels():
        print(" -", m)


if __name__ == "__main__":
    main()

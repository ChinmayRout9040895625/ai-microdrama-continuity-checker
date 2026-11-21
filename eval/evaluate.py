"""Score a checker run against the planted contradictions.

python eval/evaluate.py --planted outputs/<planted-run> --clean outputs/<clean-run> [--out eval/results.md]

A planted item counts as FOUND when some flag pairs the planted episode with one of its
source episodes AND the planted-episode quote overlaps the planted text (so a flag on the
right episodes but about something else doesn't count).
"""
import argparse
import sys
import json
from pathlib import Path

from rapidfuzz import fuzz

ROOT = Path(__file__).resolve().parent.parent
QUOTE_MATCH = 60


def load_issues(run_dir: Path) -> tuple[list[dict], dict]:
    d = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
    return d["issues"], d["meta"]


def matches(item: dict, iss: dict) -> bool:
    p, n = iss["prior"], iss["new"]
    for planted_side, other in ((n, p), (p, n)):
        if planted_side["episode"] == item["episode"] and other["episode"] in item["source_episodes"]:
            if any(fuzz.partial_ratio(planted_side["quote"].lower(), e["replace"].lower()) >= QUOTE_MATCH
                   or fuzz.partial_ratio(e["replace"].lower(), planted_side["quote"].lower()) >= QUOTE_MATCH
                   for e in item["edits"]):
                return True
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--planted", required=True)
    ap.add_argument("--clean", required=True)
    ap.add_argument("--out", default="eval/results.md")
    a = ap.parse_args()

    items = json.loads((ROOT / "data/planted.json").read_text(encoding="utf-8"))
    p_issues, p_meta = load_issues(Path(a.planted))
    c_issues, c_meta = load_issues(Path(a.clean))

    found, used = [], set()
    for it in items:
        hits = [i for i in p_issues if matches(it, i)]
        used |= {h["id"] for h in hits}
        found.append({"id": it["id"], "type": it["type"], "found": bool(hits),
                      "distance": it["episode"] - max(e for e in it["source_episodes"] if e < it["episode"]),
                      "description": it["description"],
                      "severity": hits[0]["severity"] if hits else None})
    extra = [i for i in p_issues if i["id"] not in used]
    recall = sum(f["found"] for f in found) / len(found)

    L = ["# Evaluation: planted contradictions (S2)", "",
         f"- Planted run: `{p_meta['run_id']}`, clean run: `{c_meta['run_id']}`",
         f"- Model: {p_meta['models']}", "",
         f"| Metric | Value |", "|---|---|",
         f"| Recall on planted errors | **{sum(f['found'] for f in found)}/{len(found)} ({recall:.0%})** |",
         f"| Flags on planted set not matching a planted error | {len(extra)} (see below; label by hand) |",
         f"| Flags on CLEAN set (false-alarm candidates) | {len(c_issues)} "
         f"({sum(i['could_be_intentional'] for i in c_issues)} marked 'could be intentional') |",
         f"| Facts extracted / dropped by quote check (planted) | {p_meta['facts_kept']} / {p_meta['facts_rejected']} |",
         f"| Tokens in / out (planted run) | {p_meta['usage']['input_tokens']:,} / {p_meta['usage']['output_tokens']:,} |",
         f"| Wall time (planted run) | {p_meta['wall_seconds']} s |", "",
         "## Per planted error", "", "| ID | Type | Episode gap | Found | Severity | Description |", "|---|---|---|---|---|---|"]
    L += [f"| {f['id']} | {f['type']} | {f['distance']} | {'✅' if f['found'] else '❌'} | {f['severity'] or ''} | {f['description']} |" for f in found]

    def fmt(i):
        flag = " ⚑intentional?" if i["could_be_intentional"] else ""
        return (f"- **Ep{i['prior']['episode']} vs Ep{i['new']['episode']}** [{i['severity']}/{i['issue_type']}{flag}] "
                f"\"{i['prior']['quote']}\" vs \"{i['new']['quote']}\": {i['explanation']}")

    L += ["", "## Extra flags on planted set", ""] + ([fmt(i) for i in extra] or ["_none_"])
    L += ["", "## Flags on clean set", ""] + ([fmt(i) for i in c_issues] or ["_none_"])
    out = ROOT / a.out
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    (out.with_suffix(".json")).write_text(json.dumps({"recall": recall, "per_item": found, "extra_flags": len(extra),
                                                       "clean_flags": len(c_issues)}, indent=2), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

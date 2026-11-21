"""Step 7: write report.md / report.json / bible.json."""
import json
from pathlib import Path

from .schemas import Issue

SEV_ORDER = {"high": 0, "medium": 1, "low": 2}
SEV_ICON = {"high": "🔴 HIGH", "medium": "🟠 MEDIUM", "low": "🟡 LOW"}


def sort_issues(issues: list[Issue]) -> list[Issue]:
    return sorted(issues, key=lambda i: (SEV_ORDER[i.severity], i.could_be_intentional, i.new.episode, i.prior.episode))


def recurring(issues: list[Issue], min_count: int = 3) -> list[dict]:
    """Group flags about the same character + fact type (e.g. one character's age drifting everywhere)."""
    groups: dict[tuple[str, str], list[Issue]] = {}
    for i in issues:
        key = (i.new.entity_key or i.new.entity.lower(), i.issue_type)
        groups.setdefault(key, []).append(i)
    out = []
    for (_, typ), its in groups.items():
        if len(its) >= min_count:
            eps = sorted({e for i in its for e in (i.prior.episode, i.new.episode)})
            out.append({"entity": its[0].new.entity, "issue_type": typ, "count": len(its), "episodes": eps})
    return sorted(out, key=lambda g: -g["count"])


def to_markdown(series: str, issues: list[Issue], meta: dict) -> str:
    lines = [
        f"# Continuity report: {series}",
        "",
        f"- Episodes checked: **{meta['episodes']}**  ·  facts extracted: **{meta['facts_kept']}** "
        f"(+{meta['facts_rejected']} dropped: quote not found in script)",
        f"- Issues flagged: **{len(issues)}**  "
        + "  ".join(f"{SEV_ICON[s]}: {sum(i.severity == s for i in issues)}" for s in SEV_ORDER),
        f"- Model: `{meta['provider']}` / `{meta['models']}`  ·  run: {meta['run_id']}",
        "",
        "> Each flag cites two lines from the script. Check both, then mark it **Fix**, **Intentional twist**, or **Not an issue**.",
        "",
    ]
    groups = recurring(issues)
    if groups:
        lines += ["## Recurring problems (fix these once, series-wide)", "",
                  "| Character | Fact type | Flags | Episodes involved |", "|---|---|---|---|"]
        lines += [f"| {g['entity']} | {g['issue_type']} | {g['count']} | {', '.join(map(str, g['episodes']))} |" for g in groups]
        lines += ["", "## All flags", ""]
    if not issues:
        lines.append("_No continuity issues found._")
    for n, i in enumerate(sort_issues(issues), start=1):
        twist = "  ·  ⚑ could be intentional" if i.could_be_intentional else ""
        lines += [
            f"## {n}. {SEV_ICON[i.severity]} · {i.issue_type} · {i.new.entity} (Ep {i.prior.episode} vs Ep {i.new.episode}){twist}",
            "",
            f"| | Episode | Line | Fact |",
            f"|---|---|---|---|",
            f'| Earlier | {i.prior.episode} | "{i.prior.quote}" | {i.prior.value} |',
            f'| Later | {i.new.episode} | "{i.new.quote}" | {i.new.value} |',
            "",
            f"**Why:** {i.explanation}",
            "",
            f"**Suggested fix:** {i.suggested_fix}",
            "",
        ]
    return "\n".join(lines)


def write(out_dir: Path, series: str, issues: list[Issue], bible: dict, meta: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.md").write_text(to_markdown(series, issues, meta), encoding="utf-8")
    (out_dir / "report.json").write_text(
        json.dumps({"meta": meta, "issues": [i.model_dump() for i in sort_issues(issues)]}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (out_dir / "bible.json").write_text(json.dumps(bible, indent=2, ensure_ascii=False), encoding="utf-8")

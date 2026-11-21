"""Step 5+6: compare each episode's facts with relevant earlier facts (LLM), then
validate every returned fact ID in code so the report can only cite grounded quotes."""
from .llm import LLM
from .prompts import CHECK_SYSTEM, CHECK_USER
from .schemas import CheckOut, Episode, Fact, Issue


def _fmt(f: Fact) -> str:
    tgt = f" -> {f.target}" if f.target else ""
    return f'{f.id} | Ep{f.episode} | {f.entity} [{f.category}{tgt}] {f.value} | "{f.quote}"'


def check_episode(llm: LLM, ep: Episode, new: list[Fact], prior: list[Fact]) -> tuple[list[Issue], list[dict], str]:
    """Return (valid issues, dropped issues with reason, raw LLM JSON)."""
    if not new or not prior:
        return [], [], ""
    out, raw = llm.structured_call(
        "check",
        CHECK_SYSTEM,
        CHECK_USER.format(
            prior="\n".join(_fmt(f) for f in prior),
            new="\n".join(_fmt(f) for f in new),
            number=ep.number,
            text=ep.text,
        ),
        CheckOut,
    )
    prior_by_id = {f.id: f for f in prior}
    new_by_id = {f.id: f for f in new}
    issues, dropped, seen = [], [], set()
    for it in out.issues:
        p, n = prior_by_id.get(it.prior_fact_id.strip()), new_by_id.get(it.new_fact_id.strip())
        if p is None or n is None:
            dropped.append({"reason": "unknown fact id", **it.model_dump()})
            continue
        if not it.is_real_contradiction:
            dropped.append({"reason": "model retracted (is_real_contradiction=false)", **it.model_dump()})
            continue
        if (p.id, n.id) in seen:
            continue
        seen.add((p.id, n.id))
        issues.append(
            Issue(
                id=f"{p.id}~{n.id}",
                prior=p,
                new=n,
                issue_type=it.issue_type,
                severity=it.severity,
                explanation=it.explanation,
                could_be_intentional=it.could_be_intentional,
                suggested_fix=it.suggested_fix,
            )
        )
    return issues, dropped, raw

"""Step 2+3: per-episode fact extraction (LLM) and quote grounding (code).

Grounding: each quote the model returns is fuzzy-matched against the episode text. If it
matches (score >= QUOTE_MIN_SCORE) the quote is REPLACED by the exact span from the script,
so the report only ever shows text that is really in the episode. Otherwise the fact is dropped.
"""
import re

from rapidfuzz import fuzz

from .llm import LLM
from .prompts import EXTRACT_SYSTEM, EXTRACT_USER
from .schemas import CharacterOut, Episode, EpisodeFactsOut, Fact

QUOTE_MIN_SCORE = 85.0

_TRANS = {"‘": "'", "’": "'", "“": '"', "”": '"', "—": "-", "–": "-"}


def _norm_with_map(s: str) -> tuple[str, list[int]]:
    """Lowercase, unify quotes/dashes, collapse whitespace; keep a map back to original indices."""
    out, idx, prev_space = [], [], False
    for i, ch in enumerate(s):
        ch = _TRANS.get(ch, ch)
        if ch.isspace():
            if prev_space or not out:
                continue
            ch, prev_space = " ", True
        else:
            prev_space = False
        out.append(ch.lower())
        idx.append(i)
    return "".join(out), idx


def ground_quote(quote: str, text: str) -> tuple[float, str]:
    """Return (match score 0-100, exact span from `text`)."""
    q, _ = _norm_with_map(re.sub(r"<[^>]*>", "", quote).strip().strip("}{<>/\"' "))
    if len(q) < 8:
        return 0.0, quote
    t, idx = _norm_with_map(text)
    al = fuzz.partial_ratio_alignment(q, t)
    if al is None or al.score < QUOTE_MIN_SCORE:
        return (al.score if al else 0.0), quote
    start, end = idx[al.dest_start], idx[al.dest_end - 1] + 1
    # widen to whole words and stay on the same line
    while start > 0 and text[start - 1].isalnum():
        start -= 1
    while end < len(text) and text[end].isalnum():
        end += 1
    span = text[start:end].strip()
    return al.score, span


def extract_episode(llm: LLM, ep: Episode) -> tuple[list[CharacterOut], list[Fact], list[Fact], str]:
    """Return (characters, grounded facts, rejected facts, raw LLM JSON)."""
    out, raw = llm.structured_call(
        "extract",
        EXTRACT_SYSTEM,
        EXTRACT_USER.format(number=ep.number, title=ep.title, text=ep.text),
        EpisodeFactsOut,
    )
    kept, rejected = [], []
    for i, f in enumerate(out.facts, start=1):
        score, span = ground_quote(f.quote, ep.text)
        fact = Fact(
            id=f"E{ep.number:02d}-F{i:02d}",
            episode=ep.number,
            entity=f.entity.strip(),
            category=f.category,
            target=(f.target or "").strip() or None,
            value=f.value.strip(),
            quote=span,
            quote_score=score,
        )
        (kept if score >= QUOTE_MIN_SCORE else rejected).append(fact)
    return out.characters, kept, rejected, raw

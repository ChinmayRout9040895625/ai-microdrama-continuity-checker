"""Drift experiment: draft a microdrama episode by episode with LIMITED context, the way a
cheap generation pipeline might, then run the checker on it.

Each episode call sees: the premise, the character names, and a 2-3 sentence summary of the
PREVIOUS episode only. It never sees earlier scripts.

python eval/generate_series.py --episodes 12 --out data/S1_generated
"""
import argparse
import sys
from pathlib import Path

from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from continuity_checker.config import get_settings  # noqa: E402
from continuity_checker.llm import LLM  # noqa: E402

PREMISE = """Title: "The Housekeeper's Secret"
Genre: vertical microdrama (romance / revenge), episodes of about 60 seconds, US audience.
Premise: Nora Bell, a single mother working as a housekeeper at the Grandview Hotel in Boston, discovers that the
hotel's new owner, Julian Ashford, is the man who vanished the night before their wedding years ago. Her son Leo is
his child, and Julian doesn't know. Julian's mother, Celeste Ashford, and his fiancee, Sienna Vale, will do anything
to keep Nora away.
Main characters: Nora Bell, Leo Bell, Julian Ashford, Celeste Ashford, Sienna Vale, Marcus (hotel manager)."""

SYSTEM = """You are a writer for a vertical microdrama studio. Write ONE episode of about 250-320 words in
screenplay format with timestamps like [00:00] ... [01:00]. Include concrete specifics (ages, years, amounts,
places, job titles) the way real scripts do. Open on a hook, end on a cliffhanger."""

USER = """{premise}

Previously (episode {prev}): {summary}

Write episode {n} of {total}. Then give a 2-3 sentence summary of THIS episode for the next writer."""


class Draft(BaseModel):
    script: str = Field(description="The full episode script, starting with 'EPISODE n - \"Title\"'")
    summary: str = Field(description="2-3 sentence summary of this episode")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=12)
    ap.add_argument("--out", default="data/S1_generated")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    llm = LLM(get_settings())
    summary = "This is the first episode."
    for n in range(1, a.episodes + 1):
        d, _ = llm.structured_call(
            "generate", SYSTEM,
            USER.format(premise=PREMISE, prev=n - 1 if n > 1 else "-", summary=summary, n=n, total=a.episodes),
            Draft,
        )
        (out / f"ep{n:02d}.txt").write_text(d.script.strip() + "\n", encoding="utf-8")
        summary = d.summary
        print(f"ep{n:02d}: {summary}")
    print(f"usage: {llm.usage.as_dict()}")


if __name__ == "__main__":
    main()

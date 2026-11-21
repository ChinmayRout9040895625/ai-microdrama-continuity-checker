"""Load episodes from a folder (one file per episode) or one file with 'EPISODE n' headings."""
import re
from pathlib import Path

from .schemas import Episode

HEADING = re.compile(r"^\s*#*\s*(?:EPISODE|Episode|EP|Ep)\.?\s*(\d+)\b[^\n]*$", re.MULTILINE)
EXTS = {".txt", ".md", ".fountain"}


def split_text(text: str) -> list[Episode]:
    matches = list(HEADING.finditer(text))
    if not matches:
        return [Episode(number=1, title="Episode 1", text=text.strip())]
    eps = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        eps.append(Episode(number=int(m.group(1)), title=m.group(0).strip(" #"), text=text[m.start():end].strip()))
    return eps


def load(path: str | Path) -> list[Episode]:
    p = Path(path)
    if p.is_file():
        eps = split_text(p.read_text(encoding="utf-8"))
    elif p.is_dir():
        files = sorted(f for f in p.iterdir() if f.suffix.lower() in EXTS and not f.name.startswith("_"))
        if not files:
            raise FileNotFoundError(f"No .txt/.md episode files in {p}")
        eps = []
        for idx, f in enumerate(files, start=1):
            text = f.read_text(encoding="utf-8")
            m = HEADING.search(text) or re.search(r"(\d+)", f.stem)
            num = int(m.group(1)) if m else idx
            eps.append(Episode(number=num, title=f.stem, text=text.strip()))
    else:
        raise FileNotFoundError(p)

    eps.sort(key=lambda e: e.number)
    nums = [e.number for e in eps]
    if len(set(nums)) != len(nums):
        raise ValueError(f"Duplicate episode numbers: {nums}")
    return eps

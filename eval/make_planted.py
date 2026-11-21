"""Build data/S2_planted from data/S2_clean by applying the edits in data/planted.json.
Each `find` must occur exactly once in its episode, so the planted set is reproducible."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN, PLANTED, SPEC = ROOT / "data/S2_clean", ROOT / "data/S2_planted", ROOT / "data/planted.json"


def main() -> None:
    if PLANTED.exists():
        shutil.rmtree(PLANTED)
    shutil.copytree(CLEAN, PLANTED)
    for item in json.loads(SPEC.read_text(encoding="utf-8")):
        f = PLANTED / f"ep{item['episode']:02d}.txt"
        text = f.read_text(encoding="utf-8")
        for e in item["edits"]:
            n = text.count(e["find"])
            assert n == 1, f"{item['id']}: '{e['find']}' found {n} times in {f.name}"
            text = text.replace(e["find"], e["replace"])
        f.write_text(text, encoding="utf-8")
        print(f"{item['id']} planted in {f.name}: {item['description']}")


if __name__ == "__main__":
    main()

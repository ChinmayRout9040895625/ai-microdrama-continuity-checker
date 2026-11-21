"""Usage:  python cli.py <episodes-folder-or-file> [--out outputs] [--provider anthropic|ollama]"""
import argparse
import os
import sys


def main() -> None:
    ap = argparse.ArgumentParser(description="Microdrama script continuity checker")
    ap.add_argument("input", help="Folder of episode files (ep01.txt ...) or one file with 'EPISODE n' headings")
    ap.add_argument("--out", default="outputs", help="Output root folder")
    ap.add_argument("--provider", choices=["anthropic", "ollama"], help="Override LLM_PROVIDER from .env")
    args = ap.parse_args()
    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider

    from continuity_checker.pipeline import run  # import after env override

    out = run(args.input, args.out)
    print((out / "report.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

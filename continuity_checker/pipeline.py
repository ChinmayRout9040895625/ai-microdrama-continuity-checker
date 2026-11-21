"""Orchestrates the whole run. Used by both cli.py and app.py."""
import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Callable

from . import ingest, ledger, report
from .check import check_episode
from .config import PROMPT_VERSION, Settings, get_settings
from .extract import extract_episode
from .llm import LLM


def run(
    input_path: str | Path,
    out_root: str | Path = "outputs",
    settings: Settings | None = None,
    progress: Callable[[str], None] = print,
) -> Path:
    s = settings or get_settings()
    input_path = Path(input_path)
    series = input_path.stem if input_path.is_file() else input_path.name
    run_id = f"{series}_{datetime.now():%Y%m%d-%H%M%S}"
    out_dir = Path(out_root) / run_id
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    episodes = ingest.load(input_path)
    progress(f"Loaded {len(episodes)} episodes from {input_path}")
    llm = LLM(s)

    # --- Step 2-3: extract facts per episode (parallel) ---
    def _extract(ep):
        return ep.number, extract_episode(llm, ep)

    chars_by_ep, facts_by_ep, rejected = {}, {}, []
    with ThreadPoolExecutor(max_workers=s.max_workers) as pool:
        for num, (chars, kept, rej, raw) in pool.map(_extract, episodes):
            chars_by_ep[num], facts_by_ep[num] = chars, kept
            rejected += rej
            (raw_dir / f"extract_ep{num:02d}.json").write_text(raw, encoding="utf-8")
            progress(f"  ep {num}: {len(kept)} facts ({len(rej)} dropped, quote not found)")

    # --- Step 4: ledger ---
    manual = {}
    alias_file = (input_path if input_path.is_dir() else input_path.parent) / "_aliases.json"
    if alias_file.exists():
        manual = json.loads(alias_file.read_text(encoding="utf-8"))
    resolver = ledger.build_resolver(chars_by_ep, manual)
    all_facts = [f for fs in facts_by_ep.values() for f in fs]
    ledger.assign_keys(all_facts, resolver)

    # --- Step 5-6: check each episode against relevant earlier facts (parallel) ---
    def _check(ep):
        prior = ledger.relevant_prior(facts_by_ep, ep.number, resolver)
        return ep.number, len(prior), check_episode(llm, ep, facts_by_ep.get(ep.number, []), prior)

    issues, dropped = [], []
    with ThreadPoolExecutor(max_workers=s.max_workers) as pool:
        for num, n_prior, (iss, drp, raw) in pool.map(_check, episodes[1:]):
            issues += iss
            dropped += drp
            if raw:
                (raw_dir / f"check_ep{num:02d}.json").write_text(raw, encoding="utf-8")
            progress(f"  ep {num}: checked against {n_prior} earlier facts -> {len(iss)} issue(s)")

    # --- Step 7: report ---
    meta = {
        "run_id": run_id,
        "input": str(input_path),
        "episodes": len(episodes),
        "facts_kept": len(all_facts),
        "facts_rejected": len(rejected),
        "issues_dropped_invalid_ids": len(dropped),
        "provider": s.provider,
        "models": s.ollama_model if s.provider == "ollama" else f"extract={s.model_extract}@{s.effort_extract}, check={s.model_check}@{s.effort_check}",
        "prompt_version": PROMPT_VERSION,
        "usage": llm.usage.as_dict(),
        "wall_seconds": round(time.time() - t0, 1),
    }
    report.write(out_dir, series, issues, ledger.bible(all_facts, resolver), meta)
    (raw_dir / "rejected_facts.json").write_text(json.dumps([f.model_dump() for f in rejected], indent=2), encoding="utf-8")
    (raw_dir / "dropped_issues.json").write_text(json.dumps(dropped, indent=2), encoding="utf-8")
    (out_dir / "run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    progress(f"Done: {len(issues)} issue(s) -> {out_dir / 'report.md'}  ({meta['wall_seconds']}s, {meta['usage']})")
    return out_dir

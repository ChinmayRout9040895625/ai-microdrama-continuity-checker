"""Build a static results site (for Vercel) from what is already in the repo:
run reports in outputs/, scores in eval/, and the docs. Nothing is typed in by hand.

    pip install markdown
    python site/build_site.py            # writes site/public/
    vercel deploy site/public --prod
"""
import html
import json
import os
import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "public"
REPO = "https://github.com/ChinmayRout9040895625/ai-microdrama-continuity-checker"
LIVE_APP = os.getenv("LIVE_APP_URL", "")  # Streamlit Cloud URL, once deployed

CSS = """
:root{--ink:#1d1f23;--muted:#5d636e;--line:#e3e5e9;--bg:#fafaf8;--card:#fff;--accent:#b4232c;--ok:#1f7a4d}
@media (prefers-color-scheme: dark){:root{--ink:#e8e9eb;--muted:#a1a6af;--line:#33363c;--bg:#16181b;--card:#1e2024;--accent:#ff6b6b;--ok:#4cc38a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:980px;margin:0 auto;padding:32px 20px 64px}a{color:var(--accent)}
h1{font-size:2rem;margin:0 0 6px}h2{margin:36px 0 10px;font-size:1.3rem}h3{font-size:1.05rem}
.lede{color:var(--muted);font-size:1.08rem;max-width:720px}.btns{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}
.btn{border:1px solid var(--line);background:var(--card);padding:8px 14px;border-radius:8px;text-decoration:none;color:var(--ink);font-weight:600}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}.stat b{display:block;font-size:1.6rem}
.stat span{color:var(--muted);font-size:.9rem}
table{border-collapse:collapse;width:100%;background:var(--card);font-size:.92rem;margin:8px 0 16px}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}th{background:rgba(127,127,127,.08)}
code,pre{font-family:ui-monospace,Consolas,monospace;font-size:.88em}pre{background:var(--card);border:1px solid var(--line);padding:12px;overflow:auto;border-radius:8px}
blockquote{border-left:3px solid var(--line);margin:8px 0;padding:2px 12px;color:var(--muted)}
.crumb{font-size:.9rem;margin-bottom:16px}.note{color:var(--muted);font-size:.9rem}
"""


def page(title: str, body: str, depth: int = 0) -> str:
    up = "../" * depth
    crumb = f'<div class="crumb"><a href="{up}index.html">&larr; Overview</a> · <a href="{REPO}">GitHub</a></div>' if depth else ""
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body><main>{crumb}{body}</main></body></html>")


def md(path: Path) -> str:
    out = markdown.markdown(path.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])

    def to_github(m: "re.Match") -> str:  # repo-relative links in the markdown -> GitHub
        target = (path.parent / m.group(1)).resolve()
        try:
            rel = target.relative_to(ROOT).as_posix()
        except ValueError:
            return m.group(0)
        kind = "tree" if target.is_dir() else "blob"
        return f'href="{REPO}/{kind}/main/{rel}"'

    return re.sub(r'href="(?!https?:|#|mailto:)([^"]+)"', to_github, out)


def write(rel: str, content: str) -> None:
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)

    # ---- run reports ----
    runs = []
    for rep in sorted((ROOT / "outputs").rglob("report.md")):
        run_dir = rep.parent
        meta = json.loads((run_dir / "run_meta.json").read_text(encoding="utf-8"))
        slug = str(run_dir.relative_to(ROOT / "outputs")).replace("\\", "/").replace("/", "__")
        write(f"reports/{slug}.html", page(meta["run_id"], md(rep), depth=1))
        n_issues = len(json.loads((run_dir / "report.json").read_text(encoding="utf-8"))["issues"])
        runs.append((slug, meta, n_issues, str(run_dir.relative_to(ROOT)).replace("\\", "/")))

    # ---- docs ----
    docs = [("Solution doc", "solution_doc", ROOT / "docs/SOLUTION_DOC.md"),
            ("Problem analysis", "problem_analysis", ROOT / "docs/PROBLEM_ANALYSIS.md"),
            ("Implementation plan", "implementation_plan", ROOT / "docs/IMPLEMENTATION_PLAN.md"),
            ("Final audit", "final_audit", ROOT / "docs/FINAL_AUDIT.md"),
            ("README", "readme", ROOT / "README.md"),
            ("Drift experiment (S1) results", "results_s1", ROOT / "eval/results_S1.md"),
            ("Final evaluation (planted set)", "results_v3_final", ROOT / "eval/results_v3_final.md"),
            ("Raw outputs index", "outputs_index", ROOT / "outputs/README.md")]
    doc_links = []
    for title, slug, path in docs:
        write(f"docs/{slug}.html", page(title, md(path), depth=1))
        doc_links.append(f'<li><a href="docs/{slug}.html">{html.escape(title)}</a></li>')

    # ---- scores (from eval/*.json written by eval/evaluate.py) ----
    score_files = [("v1 (extraction effort low)", "results_v1_effort-low"), ("v2", "results_v2"), ("v2 repeat 2", "results_v2_repeat2"),
                   ("v2 repeat 3", "results_v2_repeat3"), ("final", "results_v3_final"), ("final, fresh environment", "results_fresh_env")]
    rows, recalls = [], []
    for label, name in score_files:
        d = json.loads((ROOT / f"eval/{name}.json").read_text(encoding="utf-8"))
        found = sum(i["found"] for i in d["per_item"])
        if not label.startswith("v1"):
            recalls.append(found)
        rows.append(f"<tr><td>{label}</td><td>{found}/{len(d['per_item'])}</td><td>{d['clean_flags']}</td>"
                    f"<td>{d['extra_flags']}</td></tr>")
    labels = json.loads((ROOT / "eval/S1_labels.json").read_text(encoding="utf-8"))["labels"]
    real = sum(l["label"] == "true_error" for l in labels)
    fresh_meta = json.loads((ROOT / "outputs/fresh_env/S2_planted_20261121-174434/run_meta.json").read_text(encoding="utf-8"))

    run_rows = "".join(
        f"<tr><td><a href='reports/{s}.html'>{html.escape(p)}</a></td><td>{m['episodes']}</td><td>{n}</td>"
        f"<td>{m['prompt_version']}</td><td>{m['usage']['input_tokens']:,} / {m['usage']['output_tokens']:,}</td></tr>"
        for s, m, n, p in runs)
    live = f'<a class="btn primary" href="{LIVE_APP}">Open the live app</a>' if LIVE_APP else ""

    body = f"""
<h1>Microdrama Continuity Checker</h1>
<p class="lede">AI-drafted microdramas run to 50+ one-minute episodes, and facts drift between them: ages change, a dead
father reappears, a character is "shocked" by something she already knew. This tool reads a series' episode scripts and
reports every place where a later episode contradicts an earlier one, with both lines quoted verbatim from the script,
before the episodes go to video generation.</p>
<div class="btns">{live}<a class="btn" href="{REPO}">GitHub repository</a><a class="btn" href="docs/solution_doc.html">Solution doc</a>
<a class="btn" href="reports/S1_generated_20261121-173414.html">Example report</a></div>
<p class="note">Kuku AI Generalist Assignment, Problem 3. This page is a static view of the stored results; to check new
scripts, run the app from the repository{' or use the live app' if LIVE_APP else ''}.</p>

<h2>Results</h2>
<div class="grid">
<div class="stat"><b>{min(recalls)}–{max(recalls)} / 12</b><span>planted contradictions found, {len(recalls)} runs of v2+</span></div>
<div class="stat"><b>{real} / {len(labels)}</b><span>flags on an unseen AI-drafted 12-episode series judged real errors</span></div>
<div class="stat"><b>{fresh_meta['usage']['input_tokens']//1000}k / {fresh_meta['usage']['output_tokens']//1000}k</b><span>input / output tokens for a 10-episode run (Claude Sonnet 5.5), under a minute</span></div>
</div>
<table><tr><th>Version</th><th>Planted errors found</th><th>Flags on clean script</th><th>Other flags on planted set</th></tr>{''.join(rows)}</table>
<p class="note">v1 was scored before one gold label was corrected (10/12 with the correction). Prompts were tuned on this
planted set, so these numbers are optimistic. Details: <a href="docs/results_v3_final.html">final evaluation</a>,
<a href="docs/results_s1.html">drift experiment</a>.</p>

<h2>How it works</h2>
<table>
<tr><th>Step</th><th>Done by</th></tr>
<tr><td>Split scripts into episodes; merge character aliases; pick earlier facts about the same characters</td><td>Code</td></tr>
<tr><td>Extract checkable facts per episode, each with a verbatim quote</td><td>LLM (structured JSON)</td></tr>
<tr><td>Find each quote in the script and replace it with the exact text, or drop the fact</td><td>Code</td></tr>
<tr><td>Say which new fact contradicts which earlier fact, by fact ID only</td><td>LLM</td></tr>
<tr><td>Error or deliberate twist?</td><td>Human (Fix / Intentional twist / Not an issue)</td></tr>
</table>

<h2>All run reports (unedited)</h2>
<table><tr><th>Run</th><th>Episodes</th><th>Flags</th><th>Prompt version</th><th>Tokens in / out</th></tr>{run_rows}</table>

<h2>Documents</h2>
<ul>{''.join(doc_links)}</ul>
"""
    write("index.html", page("Microdrama Continuity Checker", body))
    print(f"built {OUT}: {len(runs)} reports, {len(docs)} docs")


if __name__ == "__main__":
    main()

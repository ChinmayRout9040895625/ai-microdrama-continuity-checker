"""Streamlit UI:  streamlit run app.py"""
import json
import tempfile
from pathlib import Path

import streamlit as st

from continuity_checker.config import get_settings
from continuity_checker.pipeline import run
from continuity_checker.report import SEV_ICON

ROOT = Path(__file__).parent
SAMPLES = {p.name: p for p in sorted((ROOT / "data").iterdir()) if p.is_dir()}

st.set_page_config(page_title="Microdrama Continuity Checker", layout="wide")
st.title("Microdrama Continuity Checker")
st.caption("Upload the episode scripts of a series. Get every place where one episode contradicts another, "
           "with both lines quoted, before the scripts go to video generation.")

with st.sidebar:
    st.header("Model")
    base = get_settings()
    provider = st.selectbox("Provider", ["anthropic", "ollama"], index=0 if base.provider == "anthropic" else 1)
    if provider == "anthropic":
        m_ex = st.text_input("Extraction model", base.model_extract)
        m_ck = st.text_input("Check model", base.model_check)
        e_ex = st.selectbox("Extraction effort", ["low", "medium", "high"], index=["low", "medium", "high"].index(base.effort_extract))
        e_ck = st.selectbox("Check effort", ["low", "medium", "high"], index=["low", "medium", "high"].index(base.effort_check))
        settings = get_settings(provider=provider, model_extract=m_ex, model_check=m_ck, effort_extract=e_ex, effort_check=e_ck)
    else:
        settings = get_settings(provider=provider, ollama_model=st.text_input("Ollama model", base.ollama_model))

src = st.radio("Input", ["Sample series", "Upload episode files"], horizontal=True)
input_path = None
if src == "Sample series":
    name = st.selectbox("Sample", list(SAMPLES), index=list(SAMPLES).index("S2_planted") if "S2_planted" in SAMPLES else 0)
    input_path = SAMPLES[name]
else:
    files = st.file_uploader("Episode files (.txt / .md), one per episode, or one file with 'EPISODE n' headings",
                             type=["txt", "md"], accept_multiple_files=True)
    if files:
        tmp = Path(tempfile.mkdtemp()) / "upload"
        tmp.mkdir()
        for f in files:
            (tmp / f.name).write_bytes(f.getvalue())
        input_path = tmp if len(files) > 1 else tmp / files[0].name

if st.button("Check continuity", type="primary", disabled=input_path is None):
    log = st.empty()
    lines: list[str] = []

    def progress(msg: str) -> None:
        lines.append(msg)
        log.code("\n".join(lines[-15:]))

    with st.spinner("Reading episodes..."):
        try:
            st.session_state["run_dir"] = str(run(input_path, ROOT / "outputs", settings, progress))
        except Exception as e:  # show the error in the UI instead of a stack trace
            st.error(f"Run failed: {e}")

run_dir = st.session_state.get("run_dir")
if run_dir:
    run_dir = Path(run_dir)
    data = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
    meta, issues = data["meta"], data["issues"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Episodes", meta["episodes"])
    c2.metric("Facts (grounded)", meta["facts_kept"], f"-{meta['facts_rejected']} ungrounded", delta_color="off")
    c3.metric("Issues", len(issues))
    c4.metric("Tokens in/out", f"{meta['usage']['input_tokens']:,} / {meta['usage']['output_tokens']:,}")

    labels_file = run_dir / "labels.json"
    labels = json.loads(labels_file.read_text()) if labels_file.exists() else {}
    tab1, tab2 = st.tabs(["Issues", "Series bible"])
    with tab1:
        for i in issues:
            p, n = i["prior"], i["new"]
            title = f"{SEV_ICON[i['severity']]} · {i['issue_type']} · {n['entity']} (Ep {p['episode']} vs Ep {n['episode']})"
            if i["could_be_intentional"]:
                title += " · ⚑ could be intentional"
            with st.expander(title, expanded=i["severity"] == "high"):
                a, b = st.columns(2)
                a.markdown(f"**Ep {p['episode']}**\n\n> {p['quote']}\n\n_{p['value']}_")
                b.markdown(f"**Ep {n['episode']}**\n\n> {n['quote']}\n\n_{n['value']}_")
                st.markdown(f"**Why:** {i['explanation']}\n\n**Suggested fix:** {i['suggested_fix']}")
                opts = ["(unlabelled)", "Fix", "Intentional twist", "Not an issue"]
                choice = st.radio("Editor decision", opts, key=i["id"], horizontal=True,
                                  index=opts.index(labels.get(i["id"], "(unlabelled)")))
                if choice != labels.get(i["id"], "(unlabelled)"):
                    labels[i["id"]] = choice
                    labels_file.write_text(json.dumps(labels, indent=2))
        if not issues:
            st.success("No continuity issues found.")
    with tab2:
        bible = json.loads((run_dir / "bible.json").read_text(encoding="utf-8"))
        for who, facts in bible.items():
            with st.expander(f"{who} ({len(facts)} facts)"):
                st.table([{k: f[k] for k in ("episode", "category", "value", "quote")} for f in facts])
    st.download_button("Download report.md", (run_dir / "report.md").read_bytes(), "report.md")
    st.caption(f"Outputs saved in {run_dir}")

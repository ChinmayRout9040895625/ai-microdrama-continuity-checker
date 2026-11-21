# Submission: Kuku AI Generalist Assignment, Problem 3

Chinmay Rout · Problem 3 (Find your own problem): Microdrama Continuity Checker

| Item (from the brief) | Required | Link |
|---|---|---|
| Solution doc (PDF, ≤ 2 pages) | Yes | `1_Solution_Doc/Solution_Doc_Problem3.pdf` in the Drive folder |
| Prototype link | Yes | Code: https://github.com/ChinmayRout9040895625/ai-microdrama-continuity-checker · Results site: https://ai-microdrama-continuity-checker.vercel.app · Live app: [Streamlit Cloud URL, once deployed] |
| Raw outputs | Yes | `outputs/` in the GitHub repo, and `3_Raw_Outputs/` in the Drive folder |
| Walkthrough video (≤ 3 min) | Optional | [link] |

## How to run the prototype

```bash
git clone https://github.com/ChinmayRout9040895625/ai-microdrama-continuity-checker
cd ai-microdrama-continuity-checker
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        # set ANTHROPIC_API_KEY
python cli.py data/S2_planted # or: streamlit run app.py
```

The model is set in `.env` (`LLM_PROVIDER`, `MODEL_EXTRACT`, `MODEL_CHECK`), so a different model or API can be plugged in without code changes.

## Before submitting

- Fill in roll no., branch and the video link in the solution doc, then regenerate the PDF.
- Make every link open for anyone who has it: the GitHub repo must be public, and the Drive folder must be shared as "anyone with the link".

# AI CV Analyzer & Career Recommendation Platform

## How to run (Windows PowerShell)
1. Open this folder in VS Code and open a terminal inside the folder.
2. Run:

    python -m venv .venv
    .venv\Scripts\activate
    python -m pip install -r requirements.txt
    python app.py

3. Open http://127.0.0.1:5000 in your browser (Ctrl + Shift + R to refresh).

## Pages that work now
- Dashboard (CV Score and Skill Gaps cards)
- CV Analyzer (upload, text extraction, editable sections, rule-based score)
- Job Matcher (compares a job description with your CV; try samples/sample_job.txt)
- Skills Roadmap (appears after running the Job Matcher)
- Interview Prep (questions from your CV and job, plus practice feedback)
- Job Recommendations (SAMPLE jobs ranked by match; they are not real vacancies)
- Settings (save/load your profile, history, saved jobs, delete all data)

## Tests
    python -m pip install pytest
    python -m pytest tests

Press Ctrl + C in the terminal to stop the server.

## Design
The whole website uses only two colours: navy blue (#0a1f44) and white (#ffffff), taken from the supplied CV Analyzer logo. The sidebar and page header are navy; the page and cards are white. The logo in static/images is a white version made for the navy sidebar.
Logo files are in static/images (logo-icon.png, logo-full.png, favicon.png).
Design tokens (colours, font, radius) are at the top of static/css/style.css.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.interview import build_questions, evaluate_answer  # noqa: E402

CV = {
    "name": "Sara",
    "skills": "Python, Flask, Git",
    "education": "BS Information Technology, 2026 - Present",
    "experience": "None yet.",
    "projects": "Student Portal\nBuilt a portal using Flask.",
    "certifications": "",
}

JOB = """Requirements:
- Python
- SQL
Nice to have:
- Docker
"""


def test_question_groups():
    q = build_questions(CV, JOB)
    assert [t["skill"] for t in q["technical"]] == ["Python", "SQL", "Docker"]
    assert len(q["behavioral"]) == 5 and len(q["hr"]) == 5


def test_missing_skill_gets_honest_guide():
    q = build_questions(CV, JOB)
    sql = [t for t in q["technical"] if t["skill"] == "SQL"][0]
    assert "not in your CV" in sql["guide"]
    assert "Do not claim" in sql["guide"]


def test_questions_without_job_use_cv_skills():
    q = build_questions(CV, "")
    assert {t["skill"] for t in q["technical"]} == {"Python", "Flask", "Git"}


def test_no_skills_note():
    q = build_questions({"skills": "", "projects": "x"}, "")
    assert q["technical"] == [] and q["notes"]


def test_feedback_scores():
    good = ("When I worked on my group project, our team had to build a portal. I built the login page "
            "using Flask and tested it. As a result, we finished 2 days early.")
    short = "I do not know."
    assert evaluate_answer("behavioral", good)["score"] > evaluate_answer("behavioral", short)["score"]
    assert evaluate_answer("hr", short)["checks"][0]["passed"] is False

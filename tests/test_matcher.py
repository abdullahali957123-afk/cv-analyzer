import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.matcher import WEIGHTS, match_job, split_job_skills  # noqa: E402

CV = {
    "skills": "Python, Flask, Git, Communication",
    "education": "BS Information Technology, 2026 - Present",
    "experience": "None yet.",
    "projects": "Built a REST API demo",
    "certifications": "",
}

JOB = """Requirements:
- Python and Flask
- SQL
- Git
Nice to have:
- Docker
"""


def test_weights_total_100():
    assert sum(WEIGHTS.values()) == 100


def test_required_and_preferred_split():
    req, pref = split_job_skills(JOB)
    assert req == ["Flask", "Git", "Python", "SQL"]
    assert pref == ["Docker"]


def test_matched_and_missing():
    r = match_job(CV, JOB)
    status = {i["skill"]: i["status"] for i in r["required"] + r["preferred"]}
    assert status["Python"] == "matched"
    assert status["SQL"] == "missing"
    assert status["Docker"] == "missing"
    assert 0 <= r["overall"] <= 100
    assert r["missing_required_count"] == 1


def test_no_invented_skill():
    r = match_job({"skills": ""}, JOB)
    assert all(i["status"] == "missing" for i in r["required"])
    assert r["overall"] == 0


def test_no_known_skills_raises():
    try:
        match_job(CV, "We need a friendly person to join our team soon.")
    except ValueError:
        return
    assert False, "ValueError expected"

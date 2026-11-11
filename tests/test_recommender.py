import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.matcher import find_skills  # noqa: E402
from utils.recommender import job_to_text, load_jobs, options, recommend  # noqa: E402

CV = {"skills": "Python, Flask, Git, HTML, CSS", "education": "BS IT", "experience": "", "projects": "", "certifications": ""}


def test_sample_jobs_text_matches_listed_skills():
    for job in load_jobs():
        assert find_skills(job_to_text(job)) == set(job["required"]) | set(job["preferred"]), job["id"]


def test_all_jobs_labeled_sample():
    r = recommend(CV, [], [])
    assert len(r["jobs"]) == len(load_jobs())
    assert all("SAMPLE" in j["label"] for j in r["jobs"])


def test_preference_bonus_does_not_change_match():
    base = {j["id"]: j for j in recommend(CV, [], [])["jobs"]}
    pref = {j["id"]: j for j in recommend(CV, ["Design"], ["Internship"])["jobs"]}
    for i, j in pref.items():
        assert j["overall"] == base[i]["overall"]
    design = [j for j in pref.values() if j["category"] == "Design"][0]
    assert design["category_bonus"] == 10 and design["type_bonus"] == 5


def test_options():
    o = options()
    assert "Design" in o["categories"] and "Internship" in o["types"]

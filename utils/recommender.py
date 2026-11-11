"""Job recommendations from SAMPLE listings (no AI). Ranking is match % plus small preference bonuses."""
import json
import os

from utils.matcher import match_job

CATEGORY_BONUS = 10
TYPE_BONUS = 5
LABEL = "SAMPLE - not a real vacancy"


def _data_path():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_jobs.json")


def load_jobs():
    with open(_data_path(), encoding="utf-8") as f:
        return json.load(f)["jobs"]


def job_to_text(job):
    lines = ["Requirements:", "- Bachelor's degree"]
    if job.get("min_years"):
        lines.append("- %d+ years of experience" % job["min_years"])
    lines += ["- " + s for s in job["required"]]
    if job["preferred"]:
        lines.append("Nice to have:")
        lines += ["- " + s for s in job["preferred"]]
    return "\n".join(lines)


def options():
    jobs = load_jobs()
    return {
        "categories": sorted({j["category"] for j in jobs}),
        "types": sorted({j["type"] for j in jobs}),
    }


def recommend(cv, categories, types):
    results = []
    for job in load_jobs():
        m = match_job(cv, job_to_text(job))
        cat_b = CATEGORY_BONUS if categories and job["category"] in categories else 0
        type_b = TYPE_BONUS if types and job["type"] in types else 0
        results.append({
            "id": job["id"], "title": job["title"], "company": job["company"],
            "category": job["category"], "type": job["type"], "location": job["location"],
            "summary": job["summary"], "label": LABEL,
            "overall": m["overall"], "category_bonus": cat_b, "type_bonus": type_b,
            "rank_score": m["overall"] + cat_b + type_b,
            "components": m["components"], "required": m["required"], "preferred": m["preferred"],
            "gaps": m["gaps"],
        })
    results.sort(key=lambda r: (-r["rank_score"], -r["overall"], r["title"]))
    return {
        "jobs": results,
        "ranking_note": (
            "Jobs are ranked by match percentage, plus %d points if the job is in a category you chose and %d points if it is a job type you chose. "
            "The match percentage itself never includes these bonuses." % (CATEGORY_BONUS, TYPE_BONUS)
        ),
        "disclaimer": (
            "All jobs here are SAMPLE listings for demonstration. They are not real vacancies. "
            "A match percentage is not a guarantee of getting a job."
        ),
    }

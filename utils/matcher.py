"""Transparent job matching (no AI). You can change the weights in WEIGHTS below."""
import re

# Configurable weights (total 100). A part that does not apply to a job is removed and the remaining weights are scaled up.
WEIGHTS = {
    "required_skills": 50,
    "preferred_skills": 20,
    "qualification": 15,
    "experience": 15,
}

SKILLS = {
    "Python": ["python"],
    "JavaScript": ["javascript"],
    "TypeScript": ["typescript"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "Bootstrap": ["bootstrap"],
    "Flask": ["flask"],
    "Django": ["django"],
    "React": ["react", "reactjs", "react.js"],
    "Node.js": ["node.js", "nodejs"],
    "PHP": ["php"],
    "Java": ["java"],
    "C++": ["c++"],
    "C#": ["c#"],
    "SQL": ["sql"],
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MongoDB": ["mongodb"],
    "Git": ["git", "github"],
    "REST API": ["rest api", "rest apis", "restful"],
    "Docker": ["docker"],
    "Linux": ["linux"],
    "Machine Learning": ["machine learning"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Seaborn": ["seaborn"],
    "Matplotlib": ["matplotlib"],
    "Excel": ["excel"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Figma": ["figma"],
    "Data Structures": ["data structures"],
    "OOP": ["oop", "object-oriented", "object oriented"],
    "Communication": ["communication"],
    "Problem Solving": ["problem solving", "problem-solving"],
    "Teamwork": ["teamwork", "team work", "team player", "collaboration"],
}

_PATTERNS = {
    name: re.compile(
        "|".join(r"(?<![A-Za-z0-9+#])" + re.escape(a) + r"(?![A-Za-z0-9+#])" for a in aliases),
        re.IGNORECASE,
    )
    for name, aliases in SKILLS.items()
}

PREF_RE = re.compile(r"preferred|nice to have|nice-to-have|good to have|bonus|advantage|\bplus\b", re.I)
REQ_RE = re.compile(r"requirement|required|must have|must-have|qualification|what you", re.I)
MASTER_RE = re.compile(r"\b(master|masters|msc|m\.sc)\b", re.I)
BACHELOR_RE = re.compile(r"\b(bachelor|bachelors|bs|bsc|b\.sc|degree)\b", re.I)
YEARS_RE = re.compile(r"(\d+)\s*\+?\s*(?:years|year|yrs)", re.I)

PLACEHOLDERS = ("none", "no ", "n/a", "nil", "-")


def _has(text):
    t = (text or "").strip().lower()
    return len(t) > 3 and not t.startswith(PLACEHOLDERS)


def find_skills(text):
    return {name for name, pat in _PATTERNS.items() if pat.search(text or "")}


def _edu_level(text):
    if MASTER_RE.search(text or ""):
        return 2
    if BACHELOR_RE.search(text or ""):
        return 1
    return 0


def split_job_skills(job):
    """Split the job description into required and preferred skills."""
    mode = "required"
    required, preferred = set(), set()
    for raw in job.splitlines():
        line = raw.strip()
        if not line:
            continue
        is_heading = len(line) <= 45 and not line.endswith(".")
        pref = bool(PREF_RE.search(line))
        if is_heading and pref:
            mode = "preferred"
            continue
        if is_heading and REQ_RE.search(line):
            mode = "required"
            continue
        level = "preferred" if pref else mode
        found = find_skills(line)
        (preferred if level == "preferred" else required).update(found)
    preferred -= required
    return sorted(required), sorted(preferred)


def match_job(cv, job):
    required, preferred = split_job_skills(job)
    if not required and not preferred:
        raise ValueError("No recognizable skills were found in the job description. Please paste a more detailed description.")

    cv_listed = find_skills(cv.get("skills") if isinstance(cv.get("skills"), str) else ", ".join(cv.get("skills") or []))
    other_text = " ".join(str(cv.get(k) or "") for k in ("projects", "experience", "certifications", "education"))
    cv_other = find_skills(other_text)

    def classify(skills):
        items = []
        for s in skills:
            if s in cv_listed:
                items.append({"skill": s, "status": "matched", "reason": "Listed in the Skills section of your CV."})
            elif s in cv_other:
                items.append({"skill": s, "status": "partial",
                              "reason": "Not in your Skills list, but mentioned in your projects or experience. Add it to Skills only if you genuinely have it."})
            else:
                items.append({"skill": s, "status": "missing", "reason": "Not found in your CV."})
        return items

    req_items = classify(required)
    pref_items = classify(preferred)

    def ratio(items):
        if not items:
            return 0
        pts = sum(1 if i["status"] == "matched" else 0.5 if i["status"] == "partial" else 0 for i in items)
        return pts / len(items)

    comps = []  # (key, label, score 0..1, detail)
    if req_items:
        comps.append(("required_skills", "Required skills", ratio(req_items), "%d of %d matched" % (sum(i["status"] == "matched" for i in req_items), len(req_items))))
    if pref_items:
        comps.append(("preferred_skills", "Preferred skills", ratio(pref_items), "%d of %d matched" % (sum(i["status"] == "matched" for i in pref_items), len(pref_items))))

    gaps = []
    jd_level = 2 if MASTER_RE.search(job) else 1 if BACHELOR_RE.search(job) else 0
    if jd_level:
        cv_level = _edu_level(cv.get("education"))
        sc = 1 if cv_level >= jd_level else 0.5 if cv_level > 0 else 0
        comps.append(("qualification", "Qualification", sc, "The job asks for %s; your CV shows: %s" % (["", "a degree", "a master's degree"][jd_level], ["nothing found", "a degree", "a master's degree"][cv_level])))
        if cv_level < jd_level:
            gaps.append("The job asks for %s, which does not appear in your CV." % ["", "a degree", "a master's degree"][jd_level])
        elif "present" in (cv.get("education") or "").lower():
            gaps.append("Your degree is still in progress (Present). If the job requires a completed degree, check your eligibility first.")

    years = [int(y) for y in YEARS_RE.findall(job)]
    if years:
        n = max(years)
        has_exp = _has(cv.get("experience"))
        sc = (1 if n <= 1 else 0.5) if has_exp else 0
        comps.append(("experience", "Experience", sc, "The job asks for %d+ years; experience in your CV: %s" % (n, "listed" if has_exp else "not listed")))
        if n >= 2:
            gaps.append("The job asks for %d+ years of experience. Years cannot be calculated automatically from your CV, so please check this yourself." % n)
        elif not has_exp:
            gaps.append("The job asks for experience but the experience section of your CV is empty.")

    total_w = sum(WEIGHTS[k] for k, *_ in comps)
    components = []
    overall = 0.0
    for key, label, sc, detail in comps:
        w = WEIGHTS[key] / total_w * 100
        pts = w * sc
        overall += pts
        components.append({"name": label, "weight": round(w, 1), "score_pct": round(sc * 100), "points": round(pts, 1), "detail": detail})

    missing_req = [i["skill"] for i in req_items if i["status"] == "missing"]
    partial_all = [i["skill"] for i in req_items + pref_items if i["status"] == "partial"]
    steps = []
    for s in missing_req[:3]:
        steps.append("Learn %s and build a small project, then add it to your CV only after you have learned it." % s)
    for s in partial_all[:2]:
        steps.append("Add %s to your Skills section, only if you genuinely have it." % s)
    if not steps:
        steps.append("Your skills match this job well. Adding results to your project descriptions would help further.")

    return {
        "overall": round(overall),
        "components": components,
        "required": req_items,
        "preferred": pref_items,
        "gaps": gaps,
        "missing_required_count": len(missing_req),
        "next_steps": steps,
        "disclaimer": (
            "This percentage only compares the text of your CV with the job description. It is not a guarantee of getting the job "
            "or a measure of your worth. Your name, age or other personal characteristics are not used in the score."
        ),
    }

"""Rule-based CV analysis (no AI). The reason behind every score is shown."""

PLACEHOLDERS = ("none", "no ", "n/a", "nil", "-")


def _has(text):
    t = (text or "").strip().lower()
    return len(t) > 3 and not t.startswith(PLACEHOLDERS)


def _skill_list(skills):
    if isinstance(skills, str):
        skills = skills.split(",")
    return [s.strip() for s in skills if s and s.strip()]


def analyze_cv(data):
    skills = _skill_list(data.get("skills", []))
    proj_lines = [l for l in (data.get("projects") or "").splitlines() if l.strip()]
    cats = []

    # Contact (20)
    s = 0
    s += 5 if (data.get("name") or "").strip() else 0
    s += 8 if "@" in (data.get("email") or "") else 0
    s += 7 if len((data.get("phone") or "").strip()) >= 9 else 0
    cats.append({
        "name": "Contact details", "score": s, "max": 20,
        "message": "Your name, email and phone number should all be present." if s < 20 else "Contact details are complete.",
        "why": "Recruiters need a direct way to reach you.",
    })

    # Education (15)
    s = 15 if _has(data.get("education")) else 0
    cats.append({
        "name": "Education", "score": s, "max": 15,
        "message": "Add an education section (degree, university, year)." if s == 0 else "Education section is present.",
        "why": "Degrees are checked first for internships and fresher jobs.",
    })

    # Skills (25)
    n = len(skills)
    s = round(min(n, 7) / 7 * 25)
    cats.append({
        "name": "Skills", "score": s, "max": 25,
        "message": ("Only %d skills found. List at least 7 relevant skills that you genuinely have." % n) if n < 7
                   else "Good skills list (%d skills)." % n,
        "why": "Job matching is based on skills; more relevant skills improve the match.",
    })

    # Projects (20)
    if len(proj_lines) >= 4:
        s = 20
    elif proj_lines:
        s = 10
    else:
        s = 0
    cats.append({
        "name": "Projects", "score": s, "max": 20,
        "message": "Add projects, with 1-2 bullet points under each." if s == 0
                   else ("Add more detail: write 1-2 bullet points for each project." if s == 10 else "Projects are well described."),
        "why": "Students have little work experience, so projects are their biggest strength.",
    })

    # Experience (10)
    s = 10 if _has(data.get("experience")) else 0
    cats.append({
        "name": "Experience", "score": s, "max": 10,
        "message": "No experience found. If you have an internship, freelance or volunteer work, add it; otherwise do not invent anything." if s == 0
                   else "Experience section is present.",
        "why": "Experience shows that you have done real work.",
    })

    # Certifications (10)
    s = 10 if _has(data.get("certifications")) else 0
    cats.append({
        "name": "Certifications", "score": s, "max": 10,
        "message": "If you complete a course or certificate, add it here." if s == 0 else "Certifications are present.",
        "why": "Certificates show that you are willing to keep learning.",
    })

    total = sum(c["score"] for c in cats)
    if total >= 80:
        label = "Excellent"
    elif total >= 55:
        label = "Good, with room to improve"
    else:
        label = "Many sections are incomplete"

    return {
        "total": total,
        "label": label,
        "categories": cats,
        "bullet_tip": (
            "Bullet point format: 'I [built/did what] using [technology] so that [result].' "
            "Fill it with your real work. Do not write anything you did not do."
        ),
        "note": "This is a rule-based analysis (not AI). The score only checks the sections of your CV and is not a guarantee of getting a job.",
    }

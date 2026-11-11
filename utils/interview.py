"""Interview preparation (no AI). Questions come from the job description and your CV.
Feedback checks answer structure only; it cannot judge whether technical content is correct."""
import re

from utils.matcher import find_skills, split_job_skills

TECH_Q = {
    "Python": "Explain the difference between a list and a dictionary in Python, and when you would use each.",
    "JavaScript": "What is the difference between let, const and var in JavaScript?",
    "TypeScript": "What problem does TypeScript solve compared to plain JavaScript?",
    "HTML": "What are semantic HTML tags, and why do they matter?",
    "CSS": "Explain the difference between Flexbox and Grid.",
    "Bootstrap": "How does the Bootstrap grid system help build responsive pages?",
    "Flask": "How does a Flask route work, and how would you return JSON from one?",
    "Django": "What is the role of models, views and templates in Django?",
    "React": "What are props and state in React?",
    "Node.js": "What is the event loop in Node.js?",
    "PHP": "How do you handle form data submitted with POST in PHP?",
    "SQL": "What is the difference between INNER JOIN and LEFT JOIN?",
    "MySQL": "What are primary keys and foreign keys, and why are they important?",
    "PostgreSQL": "What is the difference between a SQL (relational) and a NoSQL database?",
    "MongoDB": "How is data stored in MongoDB compared with a relational database?",
    "Git": "What is a Git branch, and why do teams use branches?",
    "REST API": "What do GET, POST, PUT and DELETE mean in a REST API?",
    "Docker": "What is the difference between a Docker image and a container?",
    "Linux": "How would you check and change file permissions in Linux?",
    "Machine Learning": "What is overfitting, and how can you reduce it?",
    "Data Analysis": "Walk me through how you would analyze a new dataset.",
    "Pandas": "How would you handle missing values in a Pandas DataFrame?",
    "NumPy": "Why is a NumPy array faster than a normal Python list for calculations?",
    "Matplotlib": "How would you choose between a bar chart and a line chart?",
    "Seaborn": "When would you use a heatmap or a boxplot?",
    "Excel": "How does VLOOKUP work, and when would you use a pivot table?",
    "Power BI": "What is the difference between a report and a dashboard in Power BI?",
    "Tableau": "How would you build a simple dashboard in Tableau from a dataset?",
    "Figma": "How do components help when designing an app in Figma?",
    "Data Structures": "What is the difference between a stack and a queue?",
    "OOP": "What are the main principles of object-oriented programming?",
    "Java": "What is the difference between an interface and an abstract class in Java?",
    "C++": "What is a pointer, and why can it be dangerous?",
    "C#": "What is the difference between a class and a struct in C#?",
    "Communication": "Describe a time you explained a technical idea to someone who was not technical.",
    "Problem Solving": "How do you approach a problem you have never seen before?",
    "Teamwork": "Describe your role in a group project.",
}

BEHAVIORAL = [
    "Tell me about a time you worked in a team and faced a disagreement.",
    "Describe a project you are proud of and explain your role in it.",
    "Tell me about a time you made a mistake and how you handled it.",
    "Describe a time you had to learn something quickly.",
    "Tell me about a time you had to manage more than one deadline.",
]

HR = [
    "Tell me about yourself.",
    "Why do you want this role or internship?",
    "What are your strengths and weaknesses?",
    "Where do you see yourself in three years?",
    "Do you have any questions for us?",
]

STAR_GUIDE = ("Use the STAR format: Situation (where and when), Task (what you had to do), "
              "Action (what YOU did), Result (what happened). Use a real example from your studies, "
              "projects or group work. If you do not have one, say so honestly instead of inventing a story.")

HR_GUIDE = {
    0: "Keep it to about 1 minute: who you are, your studies, your main skills and projects, and what you are looking for.",
    1: "Mention something real about the role or company, and connect it to your skills and what you want to learn.",
    2: "Give a real strength with an example. For a weakness, name a genuine one and say what you are doing to improve it.",
    3: "Be honest and realistic: what you want to learn, and how this role helps you grow.",
    4: "Prepare 2 real questions, for example about the team, the tools they use, or how interns are supported.",
}


def _lines(text):
    return [l.strip() for l in (text or "").splitlines() if l.strip()]


def _line_for(skill, cv):
    for key in ("projects", "experience", "certifications"):
        for line in _lines(cv.get(key)):
            if skill in find_skills(line):
                return line[:160]
    return ""


def _project_titles(cv):
    titles = []
    for line in _lines(cv.get("projects")):
        if len(line) <= 70 and not line.endswith("."):
            titles.append(line)
    return titles[:2]


def _intro_sample(cv):
    parts = []
    name = (cv.get("name") or "").strip()
    edu = (_lines(cv.get("education")) or [""])[0]
    skills = cv.get("skills") or ""
    if isinstance(skills, list):
        skills = ", ".join(skills)
    top = [s.strip() for s in skills.split(",") if s.strip()][:3]
    titles = _project_titles(cv)
    parts.append("My name is %s." % name if name else "Hello, thank you for having me.")
    if edu:
        parts.append("I am studying: %s." % edu.rstrip("."))
    if top:
        parts.append("My main skills are %s." % ", ".join(top))
    if titles:
        parts.append("I have worked on projects such as %s." % " and ".join(titles))
    parts.append("I am looking for an opportunity to apply what I have learned and keep growing.")
    return ("Sample built only from your CV (edit it so it sounds like you): " + " ".join(parts))


def build_questions(cv, job=""):
    skills = cv.get("skills") or ""
    if isinstance(skills, list):
        skills = ", ".join(skills)
    cv_listed = find_skills(skills)
    other = " ".join(str(cv.get(k) or "") for k in ("projects", "experience", "certifications", "education"))
    cv_other = find_skills(other)

    ordered = []
    if (job or "").strip():
        req, pref = split_job_skills(job)
        ordered = req + pref
    if not ordered:
        ordered = sorted(cv_listed)
    ordered = ordered[:6]

    technical = []
    for s in ordered:
        q = TECH_Q.get(s) or ("What is %s, and where have you used it or where would you use it?" % s)
        if s in cv_listed or s in cv_other:
            line = _line_for(s, cv)
            guide = "Structure: 1) a one-sentence definition, 2) where you really used it, 3) one result or lesson."
            guide += (' From your CV you could mention: "%s"' % line) if line else (" Pick a real project from your CV that used %s." % s)
        else:
            guide = ("%s is not in your CV. Be honest: say you have not used it much yet, explain what you already "
                     "know about it, and how you would learn it quickly. Do not claim experience you do not have." % s)
        technical.append({"type": "technical", "skill": s, "question": q, "guide": guide})

    behavioral = []
    titles = _project_titles(cv)
    for i, q in enumerate(BEHAVIORAL):
        guide = STAR_GUIDE
        if i == 1 and titles:
            guide += ' From your CV you could talk about: "%s".' % titles[0]
        behavioral.append({"type": "behavioral", "question": q, "guide": guide})

    hr = []
    for i, q in enumerate(HR):
        guide = HR_GUIDE[i]
        if i == 0:
            guide += " " + _intro_sample(cv)
        hr.append({"type": "hr", "question": q, "guide": guide})

    notes = []
    if not technical:
        notes.append("No technical skills were found, so no technical questions were generated. Add skills to your CV or paste a job description.")
    return {"technical": technical, "behavioral": behavioral, "hr": hr, "notes": notes}


def _has(pattern, text):
    return re.search(pattern, text, re.I) is not None


def evaluate_answer(qtype, answer):
    text = (answer or "").strip()
    words = len(text.split())
    checks = []

    ok_len = 30 <= words <= 250
    checks.append({
        "label": "Answer length (30-250 words)", "passed": ok_len,
        "tip": "" if ok_len else ("Your answer is short (%d words). Add more detail." % words if words < 30
                                   else "Your answer is long (%d words). Keep the main points." % words),
    })
    first = _has(r"\b(i|my|me|i'm|i've)\b", text)
    checks.append({"label": "Speaks from your own experience (I / my)", "passed": first,
                   "tip": "" if first else "Say what YOU did or know, not only general statements."})

    if qtype == "technical":
        definition = _has(r"\b(is|are|means|used to|allows|helps|lets)\b", text)
        checks.append({"label": "Explains the idea clearly", "passed": definition,
                       "tip": "" if definition else "Start with a one-sentence explanation of the concept."})
        example = _has(r"for example|for instance|in my project|i used|i built|i created|i worked|i have used", text)
        checks.append({"label": "Gives an example", "passed": example,
                       "tip": "" if example else "Add a real example, for instance from one of your projects."})
    elif qtype == "behavioral":
        sit = _has(r"\b(when|during|while|in my|at my|last (semester|year)|project|group|team)\b", text)
        checks.append({"label": "Describes the situation", "passed": sit,
                       "tip": "" if sit else "Say where and when this happened."})
        act = _has(r"\bi (built|decided|created|wrote|led|organized|fixed|tested|asked|learned|used|planned|talked|suggested|worked|started)\b", text)
        checks.append({"label": "Describes what YOU did", "passed": act,
                       "tip": "" if act else "Explain your own actions with verbs like built, decided, fixed or organized."})
        res = _has(r"result|outcome|as a result|improved|reduced|increased|completed|finished|delivered|achieved|learned|\d", text)
        checks.append({"label": "States a result or lesson", "passed": res,
                       "tip": "" if res else "End with what happened or what you learned."})
    else:  # hr
        role = _has(r"\b(role|position|internship|company|team|opportunity|learn|grow)\b", text)
        checks.append({"label": "Connects to the role or your growth", "passed": role,
                       "tip": "" if role else "Link your answer to the role, the team or what you want to learn."})

    passed = sum(1 for c in checks if c["passed"])
    score = round(passed / len(checks) * 100)
    extra = []
    if not _has(r"\d", text) and qtype != "hr":
        extra.append("Optional: add a number (time, size, result) only if it is true.")
    return {
        "score": score,
        "checks": checks,
        "extra": extra,
        "summary": "You met %d of %d checks." % (passed, len(checks)),
        "note": ("This feedback only checks the structure of your answer. It cannot tell whether the technical content is correct. "
                 "Remove any detail that is not true for you."),
    }

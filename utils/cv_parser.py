import re

SECTION_WORDS = {
    "education": ["education", "academic background", "qualification", "qualifications"],
    "skills": ["skills", "technical skills", "key skills"],
    "experience": ["experience", "work experience", "internship", "internships", "employment"],
    "projects": ["projects", "project", "academic projects"],
    "certifications": ["certifications", "certification", "certificates", "courses"],
}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"\+?\d[\d\s\-]{8,}\d")


def detect_heading(line):
    clean = re.sub(r"[^a-zA-Z ]", "", line).strip().lower()
    if not clean or len(clean) > 30:
        return None
    for key, words in SECTION_WORDS.items():
        if clean in words:
            return key
    return None


def parse_cv(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    sections = {key: [] for key in SECTION_WORDS}
    header = []
    current = None

    for line in lines:
        heading = detect_heading(line)
        if heading:
            current = heading
            continue
        if current is None:
            header.append(line)
        else:
            sections[current].append(line)

    full_text = "\n".join(lines)
    email = EMAIL_RE.search(full_text)
    phone = PHONE_RE.search(full_text)

    skills = []
    for line in sections["skills"]:
        for part in re.split(r"[,|;•]", line):
            part = part.strip(" -")
            if part:
                skills.append(part)

    result = {
        "name": header[0] if header else "",
        "email": email.group(0) if email else "",
        "phone": phone.group(0).strip() if phone else "",
        "skills": skills,
        "education": "\n".join(sections["education"]),
        "experience": "\n".join(sections["experience"]),
        "projects": "\n".join(sections["projects"]),
        "certifications": "\n".join(sections["certifications"]),
    }

    missing = []
    if not result["email"]:
        missing.append("Email")
    if not result["phone"]:
        missing.append("Phone")
    for key in ["education", "skills", "experience", "projects", "certifications"]:
        if not result[key]:
            missing.append(key.capitalize())
    result["missing"] = missing

    return result

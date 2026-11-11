from io import BytesIO

import pdfplumber
from docx import Document
from flask import Flask, jsonify, render_template, request

from utils import db
from utils.analyzer import analyze_cv
from utils.cv_parser import parse_cv
from utils.interview import build_questions, evaluate_answer
from utils.matcher import match_job
from utils.recommender import load_jobs, options, recommend
from utils.roadmap import build_roadmap

app = Flask(__name__)
db.init_db()

MAX_SIZE = 5 * 1024 * 1024  # 5 MB
app.config["MAX_CONTENT_LENGTH"] = MAX_SIZE
ALLOWED = {"pdf", "docx"}


def extract_pdf(data):
    text = ""
    with pdfplumber.open(BytesIO(data)) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text.strip()


def extract_docx(data):
    doc = Document(BytesIO(data))
    lines = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(lines).strip()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def upload():
    file = request.files.get("cv")

    if file is None or file.filename == "":
        return jsonify({"error": "No file was received."}), 400

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED:
        return jsonify({"error": "Only PDF or DOCX files are allowed."}), 400

    data = file.read()
    if len(data) == 0:
        return jsonify({"error": "The file is empty."}), 400

    try:
        text = extract_pdf(data) if ext == "pdf" else extract_docx(data)
    except Exception:
        return jsonify({"error": "The file could not be read. It may be corrupted."}), 422

    if not text:
        return jsonify({
            "error": "No text was found in the file. It may be a scanned or image-based file."
        }), 422

    return jsonify({
        "filename": file.filename,
        "text": text,
        "sections": parse_cv(text),
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid data received."}), 400
    result = analyze_cv(data)
    if db.get_setting("save_history") == "1":
        db.add_history("CV analysis", result["total"])
    return jsonify(result)


@app.route("/api/match", methods=["POST"])
def match():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("cv"), dict):
        return jsonify({"error": "Invalid data received."}), 400
    job = str(payload.get("job", "")).strip()
    if len(job) < 30:
        return jsonify({"error": "The job description is too short. Please paste the full description."}), 400
    if len(job) > 10000:
        return jsonify({"error": "The job description is too long (maximum 10,000 characters)."}), 400
    try:
        result = match_job(payload["cv"], job)
        if db.get_setting("save_history") == "1":
            db.add_history("Job match", result["overall"])
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


@app.route("/api/roadmap", methods=["POST"])
def roadmap():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid data received."}), 400
    lists = []
    for key in ("required", "preferred"):
        lst = payload.get(key, [])
        if not isinstance(lst, list) or len(lst) > 100:
            return jsonify({"error": "Invalid data received."}), 400
        clean = []
        for it in lst:
            if not isinstance(it, dict) or not isinstance(it.get("skill"), str) \
                    or it.get("status") not in ("matched", "partial", "missing"):
                return jsonify({"error": "Invalid data received."}), 400
            clean.append({"skill": it["skill"], "status": it["status"]})
        lists.append(clean)
    return jsonify(build_roadmap(lists[0], lists[1]))


@app.route("/api/interview/questions", methods=["POST"])
def interview_questions():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("cv"), dict):
        return jsonify({"error": "Invalid data received."}), 400
    cv = payload["cv"]
    if not any(str(cv.get(k) or "").strip() for k in ("skills", "education", "projects")):
        return jsonify({"error": "Please upload your CV in CV Analyzer first."}), 400
    job = str(payload.get("job", "") or "")
    if len(job) > 10000:
        return jsonify({"error": "The job description is too long (maximum 10,000 characters)."}), 400
    return jsonify(build_questions(cv, job))


@app.route("/api/interview/feedback", methods=["POST"])
def interview_feedback():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid data received."}), 400
    qtype = payload.get("type")
    answer = str(payload.get("answer", "")).strip()
    if qtype not in ("technical", "behavioral", "hr"):
        return jsonify({"error": "Invalid data received."}), 400
    if len(answer) < 5:
        return jsonify({"error": "Please write an answer first."}), 400
    if len(answer) > 5000:
        return jsonify({"error": "The answer is too long (maximum 5,000 characters)."}), 400
    return jsonify(evaluate_answer(qtype, answer))


@app.route("/api/recommend/options")
def recommend_options():
    return jsonify(options())


@app.route("/api/recommend", methods=["POST"])
def recommend_jobs():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("cv"), dict):
        return jsonify({"error": "Invalid data received."}), 400
    cv = payload["cv"]
    if not any(str(cv.get(k) or "").strip() for k in ("skills", "education", "projects")):
        return jsonify({"error": "Please upload your CV in CV Analyzer first."}), 400
    opts = options()
    picked = []
    for key, allowed in (("categories", opts["categories"]), ("types", opts["types"])):
        lst = payload.get(key, [])
        if not isinstance(lst, list) or any(x not in allowed for x in lst):
            return jsonify({"error": "Invalid data received."}), 400
        picked.append(lst)
    return jsonify(recommend(cv, picked[0], picked[1]))


@app.route("/api/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or not isinstance(payload.get("save_history"), bool):
            return jsonify({"error": "Invalid data received."}), 400
        db.set_setting("save_history", "1" if payload["save_history"] else "0")
    titles = {j["id"]: j["title"] for j in load_jobs()}
    prof = db.get_profile()
    return jsonify({
        "save_history": db.get_setting("save_history") == "1",
        "profile": None if prof is None else {"name": prof["data"].get("name", ""), "updated_at": prof["updated_at"]},
        "history": db.list_history(),
        "saved_jobs": [
            {"job_id": s["job_id"], "title": titles.get(s["job_id"], s["job_id"]), "saved_at": s["saved_at"]}
            for s in db.list_saved_jobs()
        ],
    })


@app.route("/api/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid data received."}), 400
        if not any(str(data.get(k) or "").strip() for k in ("skills", "education", "projects")):
            return jsonify({"error": "There is no CV data to save yet. Upload your CV first."}), 400
        db.save_profile(data)
        return jsonify({"ok": True})
    prof = db.get_profile()
    if prof is None:
        return jsonify({"error": "No saved profile found."}), 404
    return jsonify(prof)


@app.route("/api/saved-jobs", methods=["POST"])
def saved_jobs_add():
    payload = request.get_json(silent=True)
    job_id = payload.get("job_id") if isinstance(payload, dict) else None
    if job_id not in {j["id"] for j in load_jobs()}:
        return jsonify({"error": "Unknown job."}), 400
    db.save_job(job_id)
    return jsonify({"ok": True})


@app.route("/api/saved-jobs/<job_id>", methods=["DELETE"])
def saved_jobs_remove(job_id):
    db.remove_job(job_id)
    return jsonify({"ok": True})


@app.route("/api/data", methods=["DELETE"])
def delete_data():
    db.delete_all()
    return jsonify({"ok": True})


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "The file is too large. Maximum size is 5 MB."}), 413


if __name__ == "__main__":
    app.run(debug=True)

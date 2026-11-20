from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader
from io import BytesIO
from collections import Counter
import re

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024
STOP = set("the is are was were a an and or of to in on for with by from at as it this that these those what when where who which why how explain describe define write about give discuss list".split())

def get_words(text):
    return [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'-]*", text)]

def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if len(s.split()) >= 3]

def keywords(text, limit=12):
    useful = [w for w in get_words(text) if len(w) > 2 and w not in STOP]
    return [w for w, _ in Counter(useful).most_common(limit)]

def rank(text, query=""):
    ss = sentences(text)
    q = {w for w in get_words(query) if w not in STOP and len(w) > 2}
    ranked = []
    for i, s in enumerate(ss):
        terms = set(w for w in get_words(s) if w not in STOP)
        score = 2 * len(terms & q) + sum(1 / (1 + sum(t in x.lower() for x in ss)) for t in terms)
        ranked.append((score, i, s))
    return [s for _, _, s in sorted(ranked, key=lambda x: (-x[0], x[1]))]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/upload-pdf", methods=["POST"])
def upload_pdf():
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify(error="Choose a PDF file first."), 400
    if not f.filename.lower().endswith(".pdf"):
        return jsonify(error="Only PDF files are accepted."), 400
    try:
        reader = PdfReader(BytesIO(f.read()))
        if reader.is_encrypted:
            return jsonify(error="Password-protected PDFs are not supported."), 400
        text = "\n".join(p.extract_text() or "" for p in reader.pages).strip()
        if not text:
            return jsonify(error="No selectable text found. Scanned PDFs need OCR."), 422
        return jsonify(text=text, pages=len(reader.pages), filename=f.filename)
    except Exception as e:
        return jsonify(error=f"Could not read PDF: {e}"), 400

@app.route("/api/summarize", methods=["POST"])
def summarize():
    d = request.get_json(silent=True) or {}
    text = str(d.get("text", "")).strip()
    ss = sentences(text)
    if len(text) < 20 or not ss:
        return jsonify(error="Please add readable study material first."), 400
    count = max(1, min(len(ss), round(len(ss) * .30)))
    chosen = set(rank(text)[:count])
    return jsonify(summary=" ".join(s for s in ss if s in chosen), keywords=keywords(text))

@app.route("/api/answer", methods=["POST"])
def answer():
    d = request.get_json(silent=True) or {}
    text, question, marks = str(d.get("text", "")).strip(), str(d.get("question", "")).strip(), str(d.get("marks", "5"))
    if not text or not question:
        return jsonify(error="Enter study material and a question."), 400
    limits = {"2": 2, "5": 4, "8": 7, "16": 12}
    if marks not in limits:
        return jsonify(error="Choose 2, 5, 8 or 16 marks."), 400
    ranked = rank(text, question)
    chosen = set(ranked[:limits[marks]])
    draft = "\n\n".join(s for s in sentences(text) if s in chosen)
    if not draft:
        draft = "No relevant sentences found in the supplied material."
    return jsonify(answer=draft, note="Rule-based answer draft selected from your text; not generative AI and not a guaranteed exam answer.")

@app.route("/api/evaluate", methods=["POST"])
def evaluate():
    d = request.get_json(silent=True) or {}
    ref, student, question = str(d.get("reference", "")).strip(), str(d.get("student_answer", "")).strip(), str(d.get("question", "")).strip()
    try:
        maximum = int(d.get("maximum", 5))
    except (TypeError, ValueError):
        maximum = 5
    if not ref or not student or not question:
        return jsonify(error="Enter the question, source material and your answer."), 400
    if maximum not in {2, 5, 8, 16}:
        return jsonify(error="Maximum marks must be 2, 5, 8 or 16."), 400
    a = {w for w in get_words(ref) if w not in STOP and len(w) > 2}
    b = {w for w in get_words(student) if w not in STOP and len(w) > 2}
    covered = a & b
    score = round(maximum * min(1, (len(covered) / max(1, len(a))) * 2.2), 1)
    missing = [w for w in keywords(ref, 15) if w not in b][:8]
    feedback = "Good keyword coverage. Check accuracy and completeness." if len(covered) / max(1, len(a)) >= .55 else "Your answer may be missing key points. Review the suggested keywords."
    return jsonify(estimated_marks=score, maximum=maximum, feedback=feedback, covered=sorted(covered)[:15], missing=missing, disclaimer="This is only a simple keyword estimate, not reliable AI grading. Your teacher's marking scheme is authoritative.")

@app.errorhandler(413)
def too_large(_):
    return jsonify(error="PDF must be 15 MB or smaller."), 413

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

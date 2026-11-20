EDUGENIUS - LOCAL WORKING STARTER
================================
Features:
- Flask backend and separate HTML, CSS, JavaScript frontend.
- Text-based PDF upload and text extraction.
- Basic extractive summary and keyword extraction.
- 2, 5, 8, 16-mark answer drafts selected from the supplied material.
- Simple keyword-overlap answer review.

IMPORTANT LIMITATIONS:
This is a working prototype, not a generative AI model. The answer drafts and mark
estimate use simple rules; they do not understand every question or guarantee exam
marks. Scanned/image-only PDFs need OCR and are not supported in this version.
A real AI provider/API integration is a separate development step.

WINDOWS SETUP:
1. Extract the ZIP.
2. Open the EduGenius_AI folder in VS Code.
3. Open Terminal > New Terminal.
4. Run: python -m pip install -r requirements.txt
5. Run: python app.py
6. Open Chrome: http://127.0.0.1:5000

Keep the terminal open while using the site. Stop it with Ctrl+C.
Do not open index.html directly; use the Flask address above.

FOLDER STRUCTURE:
app.py
requirements.txt
templates/index.html
static/style.css
static/script.js

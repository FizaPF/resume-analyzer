from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import nltk
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import os

# Download stopwords automatically (important for Render)
nltk.download('stopwords')

app = Flask(__name__)
CORS(app)

STOPWORDS = set(stopwords.words('english'))

# Home route (for testing)
@app.route('/')
def home():
    return jsonify({
        'message': 'Resume Analyzer backend is running'
    })

# Clean text
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)

    words = text.split()
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]

    return ' '.join(words)

# Extract keywords
def get_keywords(text, top_n=30):
    if not text.strip():
        return []

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=top_n
    )

    vectorizer.fit([text])

    return list(vectorizer.vocabulary_.keys())

# Analyze route
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()

    jd = data.get('jd', '')
    resume = data.get('resume', '')

    if not jd or not resume:
        return jsonify({
            'error': 'Both JD and resume are required'
        }), 400

    clean_jd = clean_text(jd)
    clean_resume = clean_text(resume)

    vectorizer = TfidfVectorizer()

    matrix = vectorizer.fit_transform([
        clean_jd,
        clean_resume
    ])

    score = int(
        cosine_similarity(
            matrix[0],
            matrix[1]
        )[0][0] * 100
    )

    jd_keywords = get_keywords(clean_jd)

    matched = [k for k in jd_keywords if k in clean_resume]
    missing = [k for k in jd_keywords if k not in clean_resume]

    return jsonify({
        'score': score,
        'matched': matched,
        'missing': missing,
        'total': len(jd_keywords)
    })

# PDF report route
@app.route('/report', methods=['POST'])
def generate_report():
    data = request.get_json()

    buffer = io.BytesIO()

    c = canvas.Canvas(buffer, pagesize=A4)

    c.setFont('Helvetica-Bold', 20)
    c.drawString(50, 800, 'Resume Keyword Analysis Report')

    c.setFont('Helvetica', 14)

    c.drawString(50, 760, f"Match Score: {data.get('score', 0)}%")

    matched = ', '.join(data.get('matched', [])[:10])
    missing = ', '.join(data.get('missing', [])[:10])

    c.drawString(50, 730, f"Matched Keywords: {matched}")
    c.drawString(50, 700, f"Missing Keywords: {missing}")

    c.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name='report.pdf',
        mimetype='application/pdf'
    )

# Run locally
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=True
    )
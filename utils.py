import json
import fitz  # PyMuPDF
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import heapq

def parse_persona_and_job(persona, job):
    return re.findall(r'\b\w+\b', persona + ' ' + job.lower())

def extract_headings_from_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data.get("outline", [])

def score_sections(headings, keywords):
    vectorizer = TfidfVectorizer()
    texts = [h["text"] for h in headings]
    corpus = texts + [" ".join(keywords)]
    tfidf = vectorizer.fit_transform(corpus)
    scores = cosine_similarity(tfidf[:-1], tfidf[-1:]).flatten()

    for i, heading in enumerate(headings):
        heading["rank"] = float(scores[i])

    ranked = heapq.nlargest(5, headings, key=lambda x: x["rank"])
    return ranked

def extract_subsections_summary(pdf_path, page_num, section_title):
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num - 1]
        text = page.get_text()
        doc.close()
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if section_title.lower() in s.lower() or len(s.split()) > 6]
        return '. '.join(sentences[:3]) + '.'
    except Exception as e:
        return ""

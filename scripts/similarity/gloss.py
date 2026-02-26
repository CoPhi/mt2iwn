"""
Gloss similarity calculation using TF-IDF cosine similarity.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .normalizer import normalize_text


def calculate_gloss_similarity(text1, text2):
    text1 = normalize_text(text1)
    text2 = normalize_text(text2)
    if not text1.strip() or not text2.strip():
        return 0.0

    vectorizer = TfidfVectorizer()
    try:
        tfidf = vectorizer.fit_transform([text1, text2])
        return cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    except ValueError as e:
        print(f"Error calculating gloss similarity: {e}")
        return 0.0
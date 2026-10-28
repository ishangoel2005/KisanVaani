"""Lightweight retrieval layer for KisanVaani.

This is a small TF-IDF RAG prototype. It keeps the knowledge base local,
retrieves relevant English passages, and returns their source metadata. It is
intentionally lightweight so it can run on a student laptop and on Streamlit
Community Cloud without downloading a large embedding model.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KB_PATH = PROJECT_ROOT / "knowledge_base" / "agri_guides.json"


def load_documents(path: Path = DEFAULT_KB_PATH) -> List[Dict]:
    """Load the curated agriculture knowledge base from JSON."""
    with Path(path).open("r", encoding="utf-8") as file:
        documents = json.load(file)

    if not isinstance(documents, list) or not documents:
        raise ValueError("The agriculture knowledge base must be a non-empty JSON list.")

    required = {"id", "title", "content", "topics", "source_title", "source_url"}
    for index, document in enumerate(documents):
        missing = required - set(document)
        if missing:
            raise ValueError(f"Knowledge-base item {index} is missing fields: {sorted(missing)}")
    return documents


def _document_text(document: Dict) -> str:
    topics = " ".join(document.get("topics", []))
    return f"{document['title']} {topics} {document['content']}"


@lru_cache(maxsize=1)
def _build_index():
    """Build and cache two small TF-IDF indexes: word and character n-grams."""
    documents = load_documents()
    texts = [_document_text(document) for document in documents]

    word_vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    char_vectorizer = TfidfVectorizer(
        lowercase=True,
        analyzer="char_wb",
        ngram_range=(3, 5),
        sublinear_tf=True,
        min_df=1,
    )

    word_matrix = word_vectorizer.fit_transform(texts)
    char_matrix = char_vectorizer.fit_transform(texts)
    return documents, word_vectorizer, word_matrix, char_vectorizer, char_matrix


def retrieve_documents(query: str, top_k: int = 4, min_score: float = 0.075) -> List[Dict]:
    """Return relevant documents ranked by a blended lexical similarity score.

    Non-English questions should be translated to English before calling this
    function. Word n-grams provide the main signal; character n-grams help with
    minor typos and word-form differences. This is retrieval, not a guarantee
    of semantic understanding, so the caller must handle low-evidence queries.
    """
    query = (query or "").strip()
    if not query:
        return []

    documents, word_vectorizer, word_matrix, char_vectorizer, char_matrix = _build_index()
    word_query = word_vectorizer.transform([query])
    char_query = char_vectorizer.transform([query])

    word_scores = cosine_similarity(word_query, word_matrix).ravel()
    char_scores = cosine_similarity(char_query, char_matrix).ravel()
    combined_scores = (0.75 * word_scores) + (0.25 * char_scores)

    ranked_indices = np.argsort(combined_scores)[::-1]
    results = []
    for index in ranked_indices[: max(1, top_k)]:
        score = float(combined_scores[index])
        if score < min_score:
            continue
        item = dict(documents[int(index)])
        item["score"] = round(score, 4)
        results.append(item)

    return results

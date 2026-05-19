"""Keyword-based NLP auto-categorization module for CivicFix.

This is intentionally free and offline. It does not use paid APIs.
The logic checks complaint descriptions against category keyword dictionaries
and returns the most relevant category with a confidence score.
"""

import re
from collections import defaultdict


CATEGORY_KEYWORDS = {
    "Waste Management": [
        "garbage", "trash", "rubbish", "waste", "plastic", "bin", "dustbin",
        "dump", "dumping", "litter", "collection", "dirty street", "solid waste"
    ],
    "Water Supply": [
        "water", "tap", "pipe", "pipeline", "leak", "leakage", "drinking water",
        "shortage", "supply", "tank", "sewage water", "contaminated water"
    ],
    "Road Maintenance": [
        "road", "pothole", "hole", "asphalt", "street", "footpath", "sidewalk",
        "traffic", "crack", "damaged road", "bridge", "parking", "speed breaker"
    ],
    "Electrical Issue": [
        "electric", "electricity", "light", "street light", "streetlight", "pole",
        "wire", "wiring", "power", "lamp", "bulb", "transformer", "voltage"
    ],
    "Drainage": [
        "drain", "drainage", "blocked drain", "clogged", "overflow", "sewer",
        "sewage", "gutter", "manhole", "flood", "water logging", "stagnant"
    ],
    "Sanitation": [
        "toilet", "washroom", "sanitation", "hygiene", "smell", "bad odor",
        "dirty toilet", "cleaning", "public toilet", "disinfection", "mosquito"
    ],
    "General Service": [
        "complaint", "service", "problem", "issue", "request", "maintenance",
        "staff", "office", "help", "general"
    ],
}


def _tokenize(text):
    """Convert text to simple lowercase tokens."""
    return re.findall(r"[a-zA-Z]+", text.lower())


def categorize_complaint(description):
    """Return the best category and confidence score for a complaint.

    The score increases when more keywords from a category appear.
    If multiple categories match, the highest scoring category is returned.
    """
    text = (description or "").lower().strip()
    if not text:
        return {"category": "General Service", "confidence": 0, "scores": {}}

    tokens = set(_tokenize(text))
    scores = defaultdict(int)

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if " " in keyword_lower:
                if keyword_lower in text:
                    scores[category] += 3
            else:
                if keyword_lower in tokens:
                    scores[category] += 2
                elif keyword_lower in text:
                    scores[category] += 1

    if not scores:
        return {"category": "General Service", "confidence": 45, "scores": {"General Service": 45}}

    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]
    total_score = sum(scores.values()) or 1

    confidence = int(min(95, max(55, round((best_score / total_score) * 100))))

    return {
        "category": best_category,
        "confidence": confidence,
        "scores": dict(scores),
    }

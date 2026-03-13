import math
import re
from collections import Counter


COMMON_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
    "you",
    "your",
    "will",
    "we",
    "our",
    "this",
    "their",
    "they",
    "has",
    "have",
    "had",
    "were",
    "was",
    "but",
    "not",
    "can",
    "using",
    "use",
    "used",
    "into",
    "across",
    "about",
    "such",
    "than",
    "other",
}

SECTION_PATTERNS = {
    "Summary": r"\b(summary|profile|professional summary|objective)\b",
    "Experience": r"\b(experience|work experience|employment history)\b",
    "Skills": r"\b(skills|technical skills|core competencies)\b",
    "Education": r"\b(education|academic background|qualifications)\b",
    "Projects": r"\b(projects|personal projects|key projects)\b",
    "Certifications": r"\b(certifications|licenses|credentials)\b",
}

ACTION_VERBS = {
    "achieved",
    "built",
    "created",
    "delivered",
    "designed",
    "developed",
    "drove",
    "enhanced",
    "executed",
    "implemented",
    "improved",
    "increased",
    "launched",
    "led",
    "managed",
    "optimized",
    "reduced",
    "scaled",
    "streamlined",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9\+\#\.-]{1,}", text.lower())


def extract_keywords(job_description: str, limit: int = 20) -> list[str]:
    tokens = [
        token
        for token in tokenize(job_description)
        if token not in COMMON_STOPWORDS and len(token) > 2
    ]
    frequencies = Counter(tokens)
    ranked_keywords = sorted(
        frequencies.items(),
        key=lambda item: (-item[1], -len(item[0]), item[0]),
    )
    return [keyword for keyword, _ in ranked_keywords[:limit]]


def detect_sections(resume_text: str) -> list[str]:
    lowered = normalize_text(resume_text)
    return [
        name
        for name, pattern in SECTION_PATTERNS.items()
        if re.search(pattern, lowered, flags=re.IGNORECASE)
    ]


def action_verb_coverage(resume_text: str) -> int:
    resume_tokens = set(tokenize(resume_text))
    matches = len(ACTION_VERBS.intersection(resume_tokens))
    return min(100, math.floor((matches / max(len(ACTION_VERBS), 1)) * 100 * 3))


def build_recommendations(
    missing_keywords: list[str],
    detected_sections: list[str],
    action_verb_score: int,
) -> list[str]:
    recommendations = []

    if missing_keywords:
        top_missing = ", ".join(missing_keywords[:5])
        recommendations.append(
            f"Add the most relevant missing keywords where they truthfully apply: {top_missing}."
        )

    if "Summary" not in detected_sections:
        recommendations.append("Add a short professional summary tailored to the target role.")

    if "Skills" not in detected_sections:
        recommendations.append("Include a dedicated skills section for ATS readability.")

    if "Projects" not in detected_sections:
        recommendations.append("Add project highlights to show practical application of your skills.")

    if action_verb_score < 45:
        recommendations.append("Strengthen bullet points with more action-oriented verbs and measurable outcomes.")

    if not recommendations:
        recommendations.append("Your resume aligns well. Focus on tailoring achievements to the role's priorities.")

    return recommendations


def build_section_feedback(detected_sections: list[str]) -> list[str]:
    feedback = []

    for section in SECTION_PATTERNS:
        if section in detected_sections:
            feedback.append(f"{section} section detected.")
        else:
            feedback.append(f"{section} section is missing or not clearly labeled.")

    return feedback


def analyze_resume(resume_text: str, job_description: str) -> dict:
    keywords = extract_keywords(job_description)
    normalized_resume = normalize_text(resume_text)

    matched_keywords = [keyword for keyword in keywords if keyword in normalized_resume]
    missing_keywords = [keyword for keyword in keywords if keyword not in normalized_resume]

    keyword_score = 0
    if keywords:
        keyword_score = (len(matched_keywords) / len(keywords)) * 100

    detected_sections = detect_sections(resume_text)
    section_score = (len(detected_sections) / len(SECTION_PATTERNS)) * 100
    verb_score = action_verb_coverage(resume_text)

    overall_score = round((keyword_score * 0.6) + (section_score * 0.25) + (verb_score * 0.15))

    return {
        "score": overall_score,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "detected_sections": detected_sections,
        "action_verb_score": verb_score,
        "recommendations": build_recommendations(
            missing_keywords,
            detected_sections,
            verb_score,
        ),
        "section_feedback": build_section_feedback(detected_sections),
    }

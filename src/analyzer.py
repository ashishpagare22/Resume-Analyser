import re
from collections import Counter


COMMON_STOPWORDS = {
    "a",
    "about",
    "across",
    "after",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "can",
    "for",
    "from",
    "had",
    "has",
    "have",
    "in",
    "into",
    "is",
    "it",
    "not",
    "of",
    "on",
    "or",
    "other",
    "our",
    "that",
    "the",
    "their",
    "they",
    "this",
    "to",
    "use",
    "used",
    "using",
    "we",
    "were",
    "will",
    "with",
    "you",
    "your",
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
    "accelerated",
    "built",
    "created",
    "delivered",
    "designed",
    "developed",
    "drove",
    "enhanced",
    "executed",
    "generated",
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

ROLE_HINTS = {
    "data": ["sql", "python", "dashboard", "analytics", "power bi", "tableau"],
    "software": ["python", "java", "react", "api", "aws", "docker"],
    "marketing": ["seo", "campaign", "content", "analytics", "crm"],
    "product": ["roadmap", "stakeholder", "kpi", "experimentation", "research"],
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9\+\#\.-]{1,}", text.lower())


def split_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def extract_keywords(job_description: str, limit: int = 24) -> list[str]:
    cleaned = normalize_text(job_description)
    phrase_matches = re.findall(
        r"\b(?:machine learning|data analysis|project management|stakeholder management|power bi|tableau|google analytics|software development|product strategy|customer success)\b",
        cleaned,
    )

    tokens = [
        token
        for token in tokenize(job_description)
        if token not in COMMON_STOPWORDS and len(token) > 2
    ]
    frequencies = Counter(tokens + phrase_matches)
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


def action_verb_score(resume_text: str) -> int:
    tokens = set(tokenize(resume_text))
    matched = len(ACTION_VERBS.intersection(tokens))
    return min(100, round((matched / max(len(ACTION_VERBS), 1)) * 260))


def quantify_impact(resume_text: str) -> tuple[int, str]:
    lines = split_lines(resume_text)
    bullet_like_lines = [
        line
        for line in lines
        if re.match(r"^(\-|\*|\d+\.)\s*", line) or len(line.split()) > 7
    ]
    quantified_lines = [
        line
        for line in bullet_like_lines
        if re.search(r"\b\d+%|\b\d+\b|\$\d+|\bmillion\b|\bk\b|\bmonths?\b|\byears?\b", line.lower())
    ]
    ratio = 0 if not bullet_like_lines else len(quantified_lines) / len(bullet_like_lines)
    score = round(min(100, ratio * 140))

    if score >= 70:
        summary = "Strong evidence of quantified achievements."
    elif score >= 40:
        summary = "Some measurable impact is present, but several bullets can be stronger."
    else:
        summary = "Most bullets describe responsibilities more than outcomes."

    return score, summary


def classify_readiness(score: int) -> str:
    if score >= 80:
        return "Strong shortlist potential"
    if score >= 65:
        return "Promising with a few targeted fixes"
    if score >= 50:
        return "Needs tailoring before applying"
    return "High risk for ATS rejection"


def infer_role_focus(job_description: str) -> str:
    lowered = normalize_text(job_description)
    for role, hints in ROLE_HINTS.items():
        if any(hint in lowered for hint in hints):
            return role
    return "general"


def build_top_fixes(
    missing_keywords: list[str],
    detected_sections: list[str],
    impact_score: int,
    keyword_score: int,
) -> list[dict]:
    fixes = []

    if missing_keywords:
        fixes.append(
            {
                "title": "Close the keyword gap",
                "detail": f"Work these missing role terms into truthful bullets, skills, or projects: {', '.join(missing_keywords[:6])}.",
            }
        )

    if "Skills" not in detected_sections:
        fixes.append(
            {
                "title": "Add a dedicated skills section",
                "detail": "List tools, platforms, and frameworks explicitly so ATS systems can parse them reliably.",
            }
        )

    if impact_score < 50:
        fixes.append(
            {
                "title": "Turn tasks into results",
                "detail": "Rewrite bullets to include numbers, percentages, timelines, revenue, cost, or scale wherever possible.",
            }
        )

    if "Summary" not in detected_sections and keyword_score < 75:
        fixes.append(
            {
                "title": "Tailor the opening summary",
                "detail": "Use the first 2 to 3 lines to mirror the role, years of experience, and strongest matching skills.",
            }
        )

    if not fixes:
        fixes.append(
            {
                "title": "Polish the strongest experience bullets",
                "detail": "Prioritize the most relevant achievements near the top and align wording more closely with the job posting.",
            }
        )

    return fixes[:4]


def build_section_feedback(detected_sections: list[str]) -> list[dict]:
    feedback = []

    for section in SECTION_PATTERNS:
        if section in detected_sections:
            feedback.append(
                {
                    "section": section,
                    "feedback": "Present and readable. Keep the strongest role-relevant details near the top.",
                }
            )
        else:
            feedback.append(
                {
                    "section": section,
                    "feedback": "Missing or not clearly labeled. Adding it can improve recruiter scanability and ATS parsing.",
                }
            )

    return feedback


def build_bullet_improvements(
    missing_keywords: list[str],
    impact_score: int,
    action_score: int,
    role_focus: str,
) -> list[dict]:
    examples = []

    if impact_score < 50:
        examples.append(
            {
                "issue": "Weak bullet style",
                "example": "Instead of 'Responsible for reports', try 'Built weekly reporting dashboard that cut manual analysis time by 35% for 4 stakeholders.'",
            }
        )

    if action_score < 45:
        examples.append(
            {
                "issue": "Low-action language",
                "example": "Start bullets with verbs like 'Led', 'Implemented', 'Optimized', or 'Delivered' before describing the result.",
            }
        )

    if missing_keywords:
        examples.append(
            {
                "issue": "Missing job language",
                "example": f"Blend in role terms naturally, for example: 'Applied {missing_keywords[0]} in a production project that improved team throughput.'",
            }
        )

    if role_focus == "data":
        examples.append(
            {
                "issue": "Data-role signal is unclear",
                "example": "Add tools plus outcomes, such as 'Used SQL and Tableau to track conversion trends and reduce weekly reporting turnaround from 1 day to 2 hours.'",
            }
        )
    elif role_focus == "software":
        examples.append(
            {
                "issue": "Engineering depth can be sharper",
                "example": "Mention stack, scale, and impact, such as 'Built REST APIs in Python and reduced average response time by 28% across 3 customer workflows.'",
            }
        )

    if not examples:
        examples.append(
            {
                "issue": "Good baseline, but tighten relevance",
                "example": "Reorder your most role-matching bullets to the top of each experience entry so recruiters see them first.",
            }
        )

    return examples[:4]


def build_summary(score: int, keyword_score: int, impact_score: int, missing_keywords: list[str]) -> str:
    if score >= 75:
        return "This resume already shows meaningful alignment with the target role and mainly needs sharper tailoring, not a rewrite."
    if keyword_score < 55 and missing_keywords:
        return f"The biggest issue is language mismatch: the resume does not yet reflect several high-priority terms such as {', '.join(missing_keywords[:3])}."
    if impact_score < 50:
        return "The resume likely undersells the candidate because it lists responsibilities more often than measurable outcomes."
    return "The resume has useful raw material, but it needs clearer role targeting and stronger evidence of impact."


def build_next_step(missing_keywords: list[str], impact_score: int, detected_sections: list[str]) -> str:
    if missing_keywords:
        return f"Revise the summary, skills, and top 3 experience bullets to include these priority terms where accurate: {', '.join(missing_keywords[:5])}."
    if impact_score < 50:
        return "Rewrite 5 bullets with numbers or percentages so the resume proves impact instead of only listing tasks."
    if "Projects" not in detected_sections:
        return "Add 1 or 2 focused project entries that show practical proof of the skills required in the job description."
    return "Do one final tailoring pass by matching the exact wording of the posting in your most relevant experience bullets."


def analyze_resume(resume_text: str, job_description: str) -> dict:
    keywords = extract_keywords(job_description)
    normalized_resume = normalize_text(resume_text)

    matched_keywords = [keyword for keyword in keywords if keyword in normalized_resume]
    missing_keywords = [keyword for keyword in keywords if keyword not in normalized_resume]

    keyword_score = round((len(matched_keywords) / len(keywords)) * 100) if keywords else 0
    detected_sections = detect_sections(resume_text)
    section_score = round((len(detected_sections) / len(SECTION_PATTERNS)) * 100)
    verb_score = action_verb_score(resume_text)
    impact_score, impact_summary = quantify_impact(resume_text)
    overall_score = round(
        (keyword_score * 0.45) + (section_score * 0.2) + (verb_score * 0.15) + (impact_score * 0.2)
    )

    role_focus = infer_role_focus(job_description)
    readiness_label = classify_readiness(overall_score)

    return {
        "score": overall_score,
        "readiness_label": readiness_label,
        "keywords": keywords,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "keyword_score": keyword_score,
        "detected_sections": detected_sections,
        "section_score": section_score,
        "action_verb_score": verb_score,
        "impact_score": impact_score,
        "impact_summary": impact_summary,
        "top_fixes": build_top_fixes(
            missing_keywords,
            detected_sections,
            impact_score,
            keyword_score,
        ),
        "section_feedback": build_section_feedback(detected_sections),
        "bullet_improvements": build_bullet_improvements(
            missing_keywords,
            impact_score,
            verb_score,
            role_focus,
        ),
        "summary": build_summary(
            overall_score,
            keyword_score,
            impact_score,
            missing_keywords,
        ),
        "next_step": build_next_step(
            missing_keywords,
            impact_score,
            detected_sections,
        ),
    }

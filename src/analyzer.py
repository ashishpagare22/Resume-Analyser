import re
from collections import Counter


ANALYSIS_MODES = {
    "balanced": {
        "label": "Balanced",
        "description": "Blend ATS keyword matching with practical recruiter readability.",
        "weights": {
            "keyword": 0.45,
            "section": 0.2,
            "action": 0.15,
            "impact": 0.2,
        },
    },
    "ats": {
        "label": "ATS-first",
        "description": "Give extra weight to keyword coverage and clean section structure.",
        "weights": {
            "keyword": 0.55,
            "section": 0.25,
            "action": 0.08,
            "impact": 0.12,
        },
    },
    "recruiter": {
        "label": "Recruiter-first",
        "description": "Prioritize impact, clarity, and bullet quality over strict ATS weighting.",
        "weights": {
            "keyword": 0.34,
            "section": 0.16,
            "action": 0.15,
            "impact": 0.35,
        },
    },
}

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

ROLE_LABELS = {
    "data": "Data and analytics",
    "software": "Software engineering",
    "marketing": "Marketing and growth",
    "product": "Product management",
    "general": "General professional fit",
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
    elif role_focus == "product":
        examples.append(
            {
                "issue": "Product ownership is undersold",
                "example": "Show decisions and results, such as 'Led roadmap prioritization that improved feature adoption by 18% across 2 release cycles.'",
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


def build_strength_signals(
    keyword_score: int,
    detected_sections: list[str],
    impact_score: int,
    matched_keywords: list[str],
    action_score: int,
) -> list[str]:
    signals = []

    if keyword_score >= 65:
        signals.append(
            f"Role language is reasonably aligned already, with {len(matched_keywords)} priority terms appearing in the resume."
        )

    if "Experience" in detected_sections:
        signals.append("The experience section is clearly labeled, which helps both ATS parsing and recruiter scanning.")

    if impact_score >= 55:
        signals.append("The resume already includes measurable outcomes in enough places to create credibility.")

    if action_score >= 50:
        signals.append("Action verbs are active enough to make the writing sound more achievement-driven than passive.")

    if not signals:
        signals.append("There is useful raw material here, and the biggest lift now comes from sharper targeting rather than a total rewrite.")

    return signals[:4]


def build_ats_risks(
    missing_keywords: list[str],
    detected_sections: list[str],
    impact_score: int,
    keyword_score: int,
    action_score: int,
) -> list[str]:
    risks = []

    if keyword_score < 60 and missing_keywords:
        risks.append(
            f"Keyword coverage is thin. Missing terms like {', '.join(missing_keywords[:4])} may reduce ATS ranking."
        )

    if "Skills" not in detected_sections:
        risks.append("A missing or unclear skills section makes exact tool matching harder for automated screening.")

    if impact_score < 50:
        risks.append("Several bullets read like responsibilities rather than results, which weakens recruiter confidence.")

    if action_score < 45:
        risks.append("Passive phrasing may make the resume feel flatter than the actual work delivered.")

    if "Summary" not in detected_sections:
        risks.append("Without a tailored summary, the most relevant fit can be easy to miss in the first scan.")

    if not risks:
        risks.append("No major ATS or recruiter red flags were detected in this pass.")

    return risks[:4]


def build_checklist(
    keyword_score: int,
    impact_score: int,
    action_score: int,
    detected_sections: list[str],
) -> list[dict]:
    return [
        {
            "label": "Keyword coverage above 60%",
            "status": keyword_score >= 60,
            "detail": "A healthier overlap with the job description improves ATS confidence.",
        },
        {
            "label": "Dedicated skills section",
            "status": "Skills" in detected_sections,
            "detail": "Explicit tools and platforms should be easy to scan in one place.",
        },
        {
            "label": "Quantified achievements present",
            "status": impact_score >= 50,
            "detail": "Recruiters respond better when the resume proves scale, results, or efficiency gains.",
        },
        {
            "label": "Action-oriented writing",
            "status": action_score >= 45,
            "detail": "Bullet points should sound active and owned, not passive or generic.",
        },
        {
            "label": "Clear summary or projects support",
            "status": "Summary" in detected_sections or "Projects" in detected_sections,
            "detail": "Strong framing near the top or project proof deeper down both help the story land faster.",
        },
    ]


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


def build_summary_template(role_focus: str, matched_keywords: list[str], missing_keywords: list[str]) -> str:
    strengths = matched_keywords[:3]
    while len(strengths) < 3:
        strengths.append(["relevant tools", "cross-functional delivery", "measurable outcomes"][len(strengths)])

    bridge_term = missing_keywords[0] if missing_keywords else "the role's top priorities"
    return (
        "Try a top-summary line like: "
        f"'Professional with hands-on experience in {strengths[0]}, {strengths[1]}, and {strengths[2]}. "
        f"Known for delivering measurable results and now targeting {ROLE_LABELS.get(role_focus, ROLE_LABELS['general']).lower()} work involving {bridge_term}.'"
    )


def build_keyword_bridge(matched_keywords: list[str], missing_keywords: list[str]) -> str:
    if matched_keywords and missing_keywords:
        return f"Connect proven work in {matched_keywords[0]} to the missing target term {missing_keywords[0]} inside a top experience bullet."
    if missing_keywords:
        return f"Use {missing_keywords[0]} in a bullet only if you can back it with a real example, tool, or project."
    return "The keyword coverage is already solid, so focus more on impact and ordering than on adding terms."


def analyze_resume(
    resume_text: str,
    job_description: str,
    analysis_mode: str = "balanced",
    keyword_limit: int = 24,
) -> dict:
    mode = ANALYSIS_MODES.get(analysis_mode, ANALYSIS_MODES["balanced"])
    keywords = extract_keywords(job_description, limit=keyword_limit)
    normalized_resume = normalize_text(resume_text)

    matched_keywords = [keyword for keyword in keywords if keyword in normalized_resume]
    missing_keywords = [keyword for keyword in keywords if keyword not in normalized_resume]

    keyword_score = round((len(matched_keywords) / len(keywords)) * 100) if keywords else 0
    detected_sections = detect_sections(resume_text)
    section_score = round((len(detected_sections) / len(SECTION_PATTERNS)) * 100)
    verb_score = action_verb_score(resume_text)
    impact_score, impact_summary = quantify_impact(resume_text)

    weights = mode["weights"]
    overall_score = round(
        (keyword_score * weights["keyword"])
        + (section_score * weights["section"])
        + (verb_score * weights["action"])
        + (impact_score * weights["impact"])
    )

    role_focus = infer_role_focus(job_description)
    readiness_label = classify_readiness(overall_score)

    return {
        "score": overall_score,
        "analysis_mode_label": mode["label"],
        "analysis_mode_description": mode["description"],
        "readiness_label": readiness_label,
        "focus_label": ROLE_LABELS.get(role_focus, ROLE_LABELS["general"]),
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
        "strength_signals": build_strength_signals(
            keyword_score,
            detected_sections,
            impact_score,
            matched_keywords,
            verb_score,
        ),
        "ats_risks": build_ats_risks(
            missing_keywords,
            detected_sections,
            impact_score,
            keyword_score,
            verb_score,
        ),
        "ats_checklist": build_checklist(
            keyword_score,
            impact_score,
            verb_score,
            detected_sections,
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
        "summary_template": build_summary_template(
            role_focus,
            matched_keywords,
            missing_keywords,
        ),
        "keyword_bridge": build_keyword_bridge(
            matched_keywords,
            missing_keywords,
        ),
    }

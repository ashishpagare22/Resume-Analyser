from io import BytesIO

import streamlit as st
from pypdf import PdfReader

from src.analyzer import analyze_resume


st.set_page_config(
    page_title="AI Resume Analyzer",
    layout="wide",
)


def load_pdf_text(uploaded_file) -> str:
    pdf_bytes = BytesIO(uploaded_file.getvalue())
    reader = PdfReader(pdf_bytes)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def render_tag_list(items: list[str], empty_message: str, tag_class: str) -> None:
    if not items:
        st.markdown(f"<p class='muted'>{empty_message}</p>", unsafe_allow_html=True)
        return

    tags = "".join(f"<span class='tag {tag_class}'>{item}</span>" for item in items)
    st.markdown(f"<div class='tag-row'>{tags}</div>", unsafe_allow_html=True)


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=DM+Sans:wght@400;500;700&display=swap');

    :root {
        --bg: #f4efe6;
        --panel: rgba(255, 250, 242, 0.92);
        --panel-strong: #fff8f0;
        --ink: #1f2937;
        --muted: #6b7280;
        --accent: #c2410c;
        --accent-soft: #ffedd5;
        --accent-strong: #9a3412;
        --success: #166534;
        --success-soft: #dcfce7;
        --warn: #9a3412;
        --warn-soft: #ffedd5;
        --border: rgba(194, 65, 12, 0.14);
        --shadow: 0 18px 55px rgba(120, 53, 15, 0.12);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(251, 191, 36, 0.18), transparent 28%),
            radial-gradient(circle at top right, rgba(251, 146, 60, 0.16), transparent 24%),
            linear-gradient(180deg, #f8f4ec 0%, var(--bg) 100%);
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2.5rem;
        max-width: 1180px;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
        color: #111827;
        letter-spacing: -0.02em;
    }

    .hero {
        background: linear-gradient(135deg, rgba(255, 247, 237, 0.96), rgba(255, 237, 213, 0.86));
        border: 1px solid var(--border);
        border-radius: 28px;
        padding: 1.75rem 1.6rem;
        box-shadow: var(--shadow);
        margin-bottom: 1.25rem;
    }

    .hero p {
        color: var(--muted);
        margin: 0.6rem 0 0;
        font-size: 1rem;
    }

    .panel {
        background: var(--panel);
        border: 1px solid rgba(255, 255, 255, 0.65);
        border-radius: 24px;
        padding: 1rem 1rem 0.75rem;
        box-shadow: var(--shadow);
        backdrop-filter: blur(8px);
        height: 100%;
    }

    .metric-card {
        background: var(--panel-strong);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 35px rgba(120, 53, 15, 0.08);
    }

    .metric-label {
        color: var(--muted);
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.45rem;
    }

    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
        line-height: 1;
    }

    .metric-helper {
        margin-top: 0.55rem;
        color: var(--muted);
        font-size: 0.92rem;
    }

    .section-card {
        background: var(--panel);
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 24px;
        padding: 1rem 1.1rem;
        margin-top: 1rem;
        box-shadow: var(--shadow);
    }

    .tag-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 0.65rem;
    }

    .tag {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 0.42rem 0.8rem;
        font-size: 0.92rem;
        font-weight: 600;
    }

    .tag.good {
        color: var(--success);
        background: var(--success-soft);
    }

    .tag.warn {
        color: var(--warn);
        background: var(--warn-soft);
    }

    .muted {
        color: var(--muted);
        margin: 0.2rem 0 0;
    }

    .list-card {
        background: rgba(255, 248, 240, 0.88);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.75rem;
    }

    .list-card strong {
        display: block;
        color: #111827;
        margin-bottom: 0.25rem;
    }

    .band {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        border-radius: 999px;
        padding: 0.45rem 0.8rem;
        background: var(--accent-soft);
        color: var(--accent-strong);
        font-weight: 700;
        margin-top: 0.65rem;
    }

    div[data-testid="stFileUploader"] {
        background: rgba(255, 248, 240, 0.86);
        border-radius: 18px;
        padding: 0.45rem;
        border: 1px dashed rgba(194, 65, 12, 0.34);
    }

    div[data-testid="stTextArea"] textarea {
        background: rgba(255, 252, 247, 0.95);
        border-radius: 16px;
        border: 1px solid rgba(194, 65, 12, 0.2);
        color: var(--ink);
    }

    div[data-testid="stButton"] button {
        border-radius: 16px;
        border: none;
        font-weight: 700;
        min-height: 3rem;
        background: linear-gradient(135deg, #c2410c, #ea580c);
        box-shadow: 0 14px 30px rgba(194, 65, 12, 0.25);
    }

    @media (max-width: 900px) {
        .hero {
            padding: 1.35rem 1.1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
        <h1>AI Resume Analyzer</h1>
        <p>Upload a PDF or paste plain text for both the resume and job description, then get a sharper ATS-style review with practical edits you can actually make.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

input_left, input_right = st.columns(2)

with input_left:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Resume Input")
    resume_pdf = st.file_uploader("Upload resume PDF", type=["pdf"], key="resume_pdf")
    resume_text = st.text_area(
        "Or paste resume text",
        height=280,
        placeholder="Paste the full resume here...",
    )
    st.markdown("</div>", unsafe_allow_html=True)

with input_right:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Job Description Input")
    job_pdf = st.file_uploader("Upload job description PDF", type=["pdf"], key="job_pdf")
    job_text = st.text_area(
        "Or paste job description text",
        height=280,
        placeholder="Paste the target job description here...",
    )
    st.markdown("</div>", unsafe_allow_html=True)

analyze_clicked = st.button("Analyze Resume", type="primary", use_container_width=True)

if analyze_clicked:
    resume_source_text = resume_text.strip()
    job_source_text = job_text.strip()

    try:
        if resume_pdf is not None:
            resume_source_text = load_pdf_text(resume_pdf)
        if job_pdf is not None:
            job_source_text = load_pdf_text(job_pdf)
    except Exception as exc:
        st.error(f"Unable to read one of the PDFs. Please try another file. Details: {exc}")
        st.stop()

    if not resume_source_text or not job_source_text:
        st.warning("Please provide both a resume and a job description as text or PDF.")
    else:
        result = analyze_resume(resume_source_text, job_source_text)

        metric_cols = st.columns(4)
        metrics = [
            ("Match Score", f"{result['score']}%", result["readiness_label"]),
            ("Keyword Match", f"{result['keyword_score']}%", f"{len(result['matched_keywords'])} of {len(result['keywords'])} priority keywords matched"),
            ("Impact Score", f"{result['impact_score']}%", result["impact_summary"]),
            ("Section Score", f"{result['section_score']}%", f"{len(result['detected_sections'])} core sections detected"),
        ]

        for col, (label, value, helper) in zip(metric_cols, metrics):
            with col:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value">{value}</div>
                        <div class="metric-helper">{helper}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown(f"<div class='band'>{result['readiness_label']}</div>", unsafe_allow_html=True)

        overview_left, overview_right = st.columns([1.1, 0.9])

        with overview_left:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.subheader("Keyword Alignment")
            render_tag_list(result["matched_keywords"], "No matched keywords yet.", "good")
            st.markdown("#### Missing Priority Keywords")
            render_tag_list(result["missing_keywords"], "No major keyword gaps detected.", "warn")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.subheader("Top Fixes")
            for item in result["top_fixes"]:
                st.markdown(
                    f"<div class='list-card'><strong>{item['title']}</strong><span>{item['detail']}</span></div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.subheader("Practical Rewrite Ideas")
            for bullet in result["bullet_improvements"]:
                st.markdown(
                    f"<div class='list-card'><strong>{bullet['issue']}</strong><span>{bullet['example']}</span></div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        with overview_right:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.subheader("Section Review")
            for line in result["section_feedback"]:
                st.markdown(
                    f"<div class='list-card'><strong>{line['section']}</strong><span>{line['feedback']}</span></div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.subheader("Recruiter Take")
            st.markdown(
                f"""
                <div class='list-card'>
                    <strong>Quick Summary</strong>
                    <span>{result['summary']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class='list-card'>
                    <strong>Next Best Step</strong>
                    <span>{result['next_step']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

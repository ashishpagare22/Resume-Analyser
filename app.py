from io import BytesIO

import streamlit as st
from pypdf import PdfReader

from src.analyzer import ANALYSIS_MODES, analyze_resume, detect_sections, extract_keywords


st.set_page_config(
    page_title="AI Resume Analyzer",
    layout="wide",
)


def ensure_session_state() -> None:
    defaults = {
        "analysis_mode": "balanced",
        "keyword_limit": 20,
        "show_previews": True,
        "resume_input": "",
        "job_description_input": "",
        "analysis_result": None,
        "analysis_signature": None,
        "resume_preview_text": "",
        "job_preview_text": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_pdf_text(uploaded_file) -> str:
    pdf_bytes = BytesIO(uploaded_file.getvalue())
    reader = PdfReader(pdf_bytes)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def render_tags(items: list[str], tone: str, empty_message: str) -> None:
    if not items:
        st.markdown(f"<p class='empty-copy'>{empty_message}</p>", unsafe_allow_html=True)
        return

    chips = "".join(f"<span class='chip {tone}'>{item}</span>" for item in items)
    st.markdown(f"<div class='chip-row'>{chips}</div>", unsafe_allow_html=True)


def render_metric_card(title: str, value: str, detail: str, tone: str = "warm") -> None:
    st.markdown(
        f"""
        <div class="metric-card {tone}">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_meter_card(title: str, value: int, detail: str, tone: str = "warm") -> None:
    st.markdown(
        f"""
        <div class="meter-card">
            <div class="meter-head">
                <span>{title}</span>
                <strong>{value}%</strong>
            </div>
            <div class="meter-track">
                <div class="meter-fill {tone}" style="width: {min(max(value, 0), 100)}%;"></div>
            </div>
            <p>{detail}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_signal_stack(title: str, items: list[str], tone: str) -> None:
    st.markdown(f"<div class='section-intro'><span>{title}</span></div>", unsafe_allow_html=True)
    for item in items:
        st.markdown(
            f"""
            <div class="signal-card {tone}">
                <div class="signal-dot"></div>
                <div>{item}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_checklist(items: list[dict]) -> None:
    for item in items:
        status_class = "ok" if item["status"] else "fix"
        status_text = "PASS" if item["status"] else "FIX"
        st.markdown(
            f"""
            <div class="check-card">
                <div class="check-main">
                    <strong>{item['label']}</strong>
                    <span>{item['detail']}</span>
                </div>
                <div class="status-pill {status_class}">{status_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="empty-shell">
            <div class="empty-card">
                <span>1. Resume Input</span>
                <strong>Upload the resume PDF or paste resume text.</strong>
                <p>If both are present, the uploaded PDF becomes the source of truth for analysis.</p>
            </div>
            <div class="empty-card">
                <span>2. Job Targeting</span>
                <strong>Paste the full job description, not just a title.</strong>
                <p>Full role requirements produce better keyword extraction and more realistic feedback.</p>
            </div>
            <div class="empty-card">
                <span>3. Practical Output</span>
                <strong>Get ATS signals, recruiter risks, and rewrite ideas.</strong>
                <p>The dashboard focuses on what to fix first, not just what is missing.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


ensure_session_state()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

    :root {
        --bg: #f4efe7;
        --card: rgba(255, 250, 244, 0.92);
        --ink: #1f2937;
        --muted: #6b7280;
        --warm: #c2410c;
        --warm-strong: #9a3412;
        --warm-soft: #ffedd5;
        --gold: #ca8a04;
        --gold-soft: #fef3c7;
        --cool: #0f766e;
        --cool-soft: #ccfbf1;
        --navy: #1d4ed8;
        --navy-soft: #dbeafe;
        --line: rgba(194, 65, 12, 0.16);
        --shadow: 0 24px 60px rgba(120, 53, 15, 0.12);
        --shadow-soft: 0 14px 34px rgba(120, 53, 15, 0.09);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(251, 191, 36, 0.18), transparent 24%),
            radial-gradient(circle at top right, rgba(244, 114, 182, 0.12), transparent 28%),
            linear-gradient(180deg, #f8f4ed 0%, var(--bg) 100%);
        color: var(--ink);
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .block-container {
        max-width: 1320px;
        padding-top: 1.6rem;
        padding-bottom: 2.5rem;
    }

    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif;
        color: #0f172a;
        letter-spacing: -0.03em;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(255, 248, 240, 0.96), rgba(252, 242, 231, 0.9));
        border-right: 1px solid rgba(194, 65, 12, 0.12);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.35rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .sidebar-card,
    .hero-shell,
    .surface-card,
    .score-card,
    .narrative-card,
    .preview-card {
        background: var(--card);
        border: 1px solid rgba(255, 255, 255, 0.72);
        box-shadow: var(--shadow);
        border-radius: 28px;
        backdrop-filter: blur(10px);
    }

    .sidebar-card {
        padding: 1rem 1rem 0.95rem;
        margin-bottom: 1rem;
    }

    .sidebar-card span,
    .section-intro span,
    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        border-radius: 999px;
        padding: 0.28rem 0.65rem;
        background: rgba(194, 65, 12, 0.08);
        color: var(--warm-strong);
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .sidebar-card h3,
    .hero-shell h1 {
        margin: 0.75rem 0 0.45rem;
    }

    .sidebar-card p,
    .hero-shell p,
    .surface-card p,
    .narrative-card p,
    .empty-card p {
        margin: 0;
        color: var(--muted);
        line-height: 1.6;
    }

    .hero-shell {
        padding: 1.45rem 1.55rem;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }

    .hero-shell::after {
        content: "";
        position: absolute;
        inset: auto -80px -90px auto;
        width: 240px;
        height: 240px;
        background: radial-gradient(circle, rgba(251, 191, 36, 0.24), transparent 68%);
        pointer-events: none;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: 1.3fr 0.7fr;
        gap: 1rem;
        align-items: stretch;
    }

    .hero-stats {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.8rem;
    }

    .hero-stat {
        background: rgba(255, 249, 240, 0.86);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 0.9rem 0.95rem;
        box-shadow: var(--shadow-soft);
    }

    .hero-stat strong {
        display: block;
        color: #111827;
        font-family: 'Outfit', sans-serif;
        font-size: 1rem;
        margin-bottom: 0.3rem;
    }

    .hero-stat span {
        color: var(--muted);
        font-size: 0.92rem;
        line-height: 1.5;
    }

    .surface-card {
        padding: 1rem 1.05rem 1.05rem;
        margin-top: 0.95rem;
    }

    .surface-card h3,
    .score-card h2,
    .narrative-card h3,
    .preview-card h3 {
        margin-top: 0.55rem;
        margin-bottom: 0.45rem;
    }

    .metric-card,
    .meter-card,
    .signal-card,
    .check-card,
    .list-card,
    .empty-card {
        animation: rise 0.45s ease;
    }

    @keyframes rise {
        from {
            opacity: 0;
            transform: translateY(8px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .metric-card {
        border-radius: 24px;
        padding: 1rem 1.05rem;
        border: 1px solid var(--line);
        box-shadow: var(--shadow-soft);
        margin-bottom: 0.9rem;
    }

    .metric-card.warm {
        background: linear-gradient(180deg, rgba(255, 247, 237, 0.98), rgba(255, 237, 213, 0.92));
    }

    .metric-card.cool {
        background: linear-gradient(180deg, rgba(240, 253, 250, 0.98), rgba(204, 251, 241, 0.9));
        border-color: rgba(15, 118, 110, 0.18);
    }

    .metric-card.navy {
        background: linear-gradient(180deg, rgba(239, 246, 255, 0.98), rgba(219, 234, 254, 0.92));
        border-color: rgba(29, 78, 216, 0.16);
    }

    .metric-card.gold {
        background: linear-gradient(180deg, rgba(255, 251, 235, 0.98), rgba(254, 243, 199, 0.92));
        border-color: rgba(202, 138, 4, 0.18);
    }

    .metric-label {
        color: var(--muted);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }

    .metric-value {
        color: #0f172a;
        font-size: 2rem;
        line-height: 1;
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .metric-detail {
        color: #475569;
        font-size: 0.95rem;
        line-height: 1.55;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 0.7rem;
    }

    .chip {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 0.46rem 0.82rem;
        font-size: 0.92rem;
        font-weight: 700;
        line-height: 1;
    }

    .chip.good {
        color: var(--cool);
        background: var(--cool-soft);
    }

    .chip.warn {
        color: var(--warm-strong);
        background: var(--warm-soft);
    }

    .chip.neutral {
        color: var(--navy);
        background: var(--navy-soft);
    }

    .empty-copy {
        color: var(--muted);
        margin: 0.35rem 0 0;
    }

    .meter-card {
        background: rgba(255, 250, 244, 0.9);
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 1rem 1.05rem;
        box-shadow: var(--shadow-soft);
        height: 100%;
    }

    .meter-head {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        align-items: center;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.75rem;
    }

    .meter-head span {
        font-size: 0.98rem;
    }

    .meter-head strong {
        font-size: 1rem;
        font-family: 'Outfit', sans-serif;
    }

    .meter-track {
        width: 100%;
        height: 12px;
        background: rgba(148, 163, 184, 0.16);
        border-radius: 999px;
        overflow: hidden;
        margin-bottom: 0.8rem;
    }

    .meter-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #fb923c, #f97316);
    }

    .meter-fill.cool {
        background: linear-gradient(90deg, #14b8a6, #0f766e);
    }

    .meter-fill.navy {
        background: linear-gradient(90deg, #3b82f6, #1d4ed8);
    }

    .meter-fill.gold {
        background: linear-gradient(90deg, #facc15, #ca8a04);
    }

    .meter-card p {
        color: var(--muted);
        font-size: 0.93rem;
        line-height: 1.55;
        margin: 0;
    }

    .score-card,
    .narrative-card,
    .preview-card {
        padding: 1.1rem 1.15rem;
        height: 100%;
    }

    .score-card .score-value {
        font-size: 4rem;
        line-height: 0.95;
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        margin: 0.65rem 0;
        color: #0f172a;
    }

    .score-band {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 0.42rem 0.82rem;
        background: var(--warm-soft);
        color: var(--warm-strong);
        font-weight: 700;
        margin-top: 0.8rem;
    }

    .mini-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.75rem;
        margin-top: 1rem;
    }

    .mini-tile {
        border-radius: 20px;
        padding: 0.9rem;
        background: rgba(255, 249, 240, 0.88);
        border: 1px solid var(--line);
    }

    .mini-tile strong {
        display: block;
        margin-bottom: 0.25rem;
        color: #111827;
        font-family: 'Outfit', sans-serif;
    }

    .mini-tile span {
        color: var(--muted);
        line-height: 1.5;
        font-size: 0.92rem;
    }

    .signal-card {
        display: grid;
        grid-template-columns: 14px 1fr;
        gap: 0.8rem;
        align-items: start;
        border-radius: 18px;
        padding: 0.85rem 0.95rem;
        margin-bottom: 0.75rem;
        border: 1px solid var(--line);
        box-shadow: var(--shadow-soft);
        line-height: 1.55;
    }

    .signal-card.positive {
        background: rgba(240, 253, 250, 0.92);
        border-color: rgba(15, 118, 110, 0.18);
    }

    .signal-card.warning {
        background: rgba(255, 247, 237, 0.92);
    }

    .signal-dot {
        width: 10px;
        height: 10px;
        border-radius: 999px;
        margin-top: 0.35rem;
        background: var(--warm);
    }

    .signal-card.positive .signal-dot {
        background: var(--cool);
    }

    .check-card,
    .list-card {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        align-items: flex-start;
        background: rgba(255, 249, 242, 0.92);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.8rem;
        box-shadow: var(--shadow-soft);
    }

    .check-main strong,
    .list-card strong {
        display: block;
        color: #111827;
        margin-bottom: 0.22rem;
        font-family: 'Outfit', sans-serif;
    }

    .check-main span,
    .list-card span {
        color: var(--muted);
        line-height: 1.55;
        font-size: 0.94rem;
    }

    .status-pill {
        flex-shrink: 0;
        border-radius: 999px;
        padding: 0.35rem 0.62rem;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.08em;
    }

    .status-pill.ok {
        color: var(--cool);
        background: var(--cool-soft);
    }

    .status-pill.fix {
        color: var(--warm-strong);
        background: var(--warm-soft);
    }

    .empty-shell {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.9rem;
        margin-top: 1rem;
    }

    .empty-card {
        background: rgba(255, 249, 242, 0.94);
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 1rem;
        box-shadow: var(--shadow-soft);
    }

    .empty-card span {
        display: inline-block;
        color: var(--warm-strong);
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.45rem;
    }

    .empty-card strong {
        display: block;
        color: #0f172a;
        font-family: 'Outfit', sans-serif;
        font-size: 1.02rem;
        margin-bottom: 0.3rem;
    }

    div[data-testid="stFileUploader"] {
        background: rgba(255, 248, 240, 0.92);
        border-radius: 20px;
        padding: 0.55rem;
        border: 1px dashed rgba(194, 65, 12, 0.36);
    }

    div[data-testid="stTextArea"] textarea {
        min-height: 290px;
        background: rgba(255, 252, 248, 0.98);
        border-radius: 20px;
        border: 1px solid rgba(194, 65, 12, 0.18);
        color: #0f172a;
    }

    div[data-testid="stTextArea"] label p,
    div[data-testid="stFileUploader"] label p,
    div[data-testid="stRadio"] label p,
    div[data-testid="stCheckbox"] label p {
        font-weight: 700;
        color: #0f172a;
    }

    div[data-testid="stButton"] button {
        min-height: 3.2rem;
        border-radius: 18px;
        border: none;
        background: linear-gradient(135deg, #ea580c, #fb923c);
        box-shadow: 0 18px 34px rgba(194, 65, 12, 0.22);
        font-weight: 800;
        letter-spacing: 0.01em;
    }

    .inline-note {
        background: rgba(255, 248, 240, 0.92);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 0.9rem 1rem;
        color: var(--muted);
        line-height: 1.55;
        height: 100%;
    }

    .section-title {
        margin: 0.2rem 0 0.35rem;
        font-family: 'Outfit', sans-serif;
        color: #0f172a;
        font-size: 1.22rem;
    }

    .section-copy {
        color: var(--muted);
        margin: 0 0 0.8rem;
        line-height: 1.55;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.55rem;
        background: rgba(255, 248, 240, 0.7);
        padding: 0.45rem;
        border-radius: 18px;
        border: 1px solid rgba(194, 65, 12, 0.14);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 14px;
        padding: 0.7rem 1rem;
        font-weight: 800;
        color: #78350f;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(251, 146, 60, 0.18), rgba(251, 191, 36, 0.22));
        color: #9a3412;
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 20px;
        background: rgba(255, 250, 244, 0.86);
        overflow: hidden;
    }

    @media (max-width: 1100px) {
        .hero-grid,
        .hero-stats,
        .empty-shell,
        .mini-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-card">
            <span>Control Panel</span>
            <h3>Guide the review</h3>
            <p>Choose how the analyzer should weigh ATS matching versus recruiter readability and impact.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.radio(
        "Scoring lens",
        options=list(ANALYSIS_MODES),
        format_func=lambda key: ANALYSIS_MODES[key]["label"],
        key="analysis_mode",
    )
    st.caption(ANALYSIS_MODES[st.session_state["analysis_mode"]]["description"])

    st.slider(
        "Priority keywords tracked",
        min_value=12,
        max_value=28,
        step=2,
        key="keyword_limit",
    )

    st.checkbox("Show extracted text previews", key="show_previews")

    st.markdown(
        """
        <div class="sidebar-card">
            <span>What Looks Strong</span>
            <h3>Practical benchmark</h3>
            <p>A strong resume mirrors the role language, uses clear sections, and proves outcomes with numbers instead of only listing tasks.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Paste-friendly job description template"):
        st.write(
            """
Role title:
Team or function:
Must-have tools:
Core responsibilities:
Success metrics:
Preferred qualifications:
"""
        )

    with st.expander("Fast bullet rewrite formula"):
        st.write("Action verb + what you changed + tool or skill used + measurable result + scope.")

st.markdown(
    """
    <div class="hero-shell">
        <div class="hero-grid">
            <div>
                <span class="eyebrow">Resume Match Studio</span>
                <h1>Make the analysis feel like a real review, not a keyword dump.</h1>
                <p>Use a resume PDF or pasted text, pair it with the full job description, and get a sharper dashboard covering ATS fit, recruiter risks, and concrete rewrite opportunities.</p>
            </div>
            <div class="hero-stats">
                <div class="hero-stat">
                    <strong>Resume PDF support</strong>
                    <span>Upload once and verify the extracted text before trusting the score.</span>
                </div>
                <div class="hero-stat">
                    <strong>Live keyword preview</strong>
                    <span>See priority role language from the job description before you even run the full analysis.</span>
                </div>
                <div class="hero-stat">
                    <strong>Action-first outputs</strong>
                    <span>Focus on top fixes, rewrite ideas, and ATS checklist items instead of vague feedback.</span>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

input_left, input_right = st.columns([1.05, 0.95], gap="large")

with input_left:
    st.markdown("<div class='section-title'>Resume Input</div>", unsafe_allow_html=True)
    st.markdown(
        "<p class='section-copy'>Upload the latest resume PDF or paste the text version. If both are present, the PDF is used for analysis.</p>",
        unsafe_allow_html=True,
    )
    resume_pdf = st.file_uploader("Resume PDF", type=["pdf"], key="resume_pdf")
    st.text_area(
        "Resume text",
        key="resume_input",
        placeholder="Paste the full resume here if you do not want to upload a PDF...",
    )

with input_right:
    st.markdown("<div class='section-title'>Job Description</div>", unsafe_allow_html=True)
    st.markdown(
        "<p class='section-copy'>Paste the full role description so the analyzer can detect requirements, keywords, and role emphasis accurately.</p>",
        unsafe_allow_html=True,
    )
    st.text_area(
        "Job description text",
        key="job_description_input",
        placeholder="Paste the target job description here...",
    )

resume_source_text = st.session_state["resume_input"].strip()
resume_source_label = "Pasted resume text"
resume_pdf_error = None

if resume_pdf is not None:
    try:
        extracted_resume_text = load_pdf_text(resume_pdf)
        if extracted_resume_text:
            resume_source_text = extracted_resume_text
            resume_source_label = f"PDF source: {resume_pdf.name}"
        else:
            resume_pdf_error = "The uploaded PDF did not produce readable text. Falling back to pasted text if available."
    except Exception as exc:
        resume_pdf_error = f"Could not read the uploaded PDF. Falling back to pasted text if available. Details: {exc}"

job_source_text = st.session_state["job_description_input"].strip()
live_sections = detect_sections(resume_source_text) if resume_source_text else []
live_keywords = extract_keywords(job_source_text, limit=st.session_state["keyword_limit"]) if job_source_text else []

if resume_pdf_error:
    st.warning(resume_pdf_error)

snapshot_cols = st.columns(4, gap="large")
with snapshot_cols[0]:
    render_metric_card(
        "Resume Source",
        "PDF" if resume_pdf is not None and not resume_pdf_error else "TEXT",
        resume_source_label,
        tone="warm",
    )
with snapshot_cols[1]:
    render_metric_card(
        "Resume Words",
        str(len(resume_source_text.split())) if resume_source_text else "--",
        "More reliable feedback usually starts with the full resume, not a short excerpt.",
        tone="navy",
    )
with snapshot_cols[2]:
    render_metric_card(
        "JD Words",
        str(len(job_source_text.split())) if job_source_text else "--",
        "Full role descriptions produce better keyword extraction and stronger suggestions.",
        tone="gold",
    )
with snapshot_cols[3]:
    render_metric_card(
        "Detected Sections",
        str(len(live_sections)),
        "Summary, experience, skills, education, projects, and certifications are checked.",
        tone="cool",
    )

preview_left, preview_right = st.columns(2, gap="large")
with preview_left:
    st.markdown(
        """
        <div class="surface-card">
            <span class="eyebrow">Live Resume Snapshot</span>
            <h3>Detected sections before analysis</h3>
            <p>This gives you a quick signal on structure even before the full score is calculated.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_tags(live_sections, "neutral", "No standard resume section labels detected yet.")

with preview_right:
    st.markdown(
        """
        <div class="surface-card">
            <span class="eyebrow">Live Job Snapshot</span>
            <h3>Priority keywords from the job description</h3>
            <p>These terms drive the matching engine and should appear naturally where they are actually true.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_tags(live_keywords[:10], "warn", "Paste a full job description to preview priority keywords.")

action_left, action_right = st.columns([0.72, 0.28], gap="large")
with action_left:
    analyze_clicked = st.button("Analyze Resume", type="primary", use_container_width=True)
with action_right:
    st.markdown(
        "<div class='inline-note'>Current scoring lens: <strong>{}</strong><br>{}</div>".format(
            ANALYSIS_MODES[st.session_state["analysis_mode"]]["label"],
            ANALYSIS_MODES[st.session_state["analysis_mode"]]["description"],
        ),
        unsafe_allow_html=True,
    )

result = st.session_state.get("analysis_result")

if analyze_clicked:
    if not resume_source_text or not job_source_text:
        st.warning("Please provide both the resume and the job description before running the analysis.")
    else:
        result = analyze_resume(
            resume_source_text,
            job_source_text,
            analysis_mode=st.session_state["analysis_mode"],
            keyword_limit=st.session_state["keyword_limit"],
        )
        st.session_state["analysis_result"] = result
        st.session_state["resume_preview_text"] = resume_source_text
        st.session_state["job_preview_text"] = job_source_text
        st.session_state["analysis_signature"] = {
            "resume_text": resume_source_text,
            "job_text": job_source_text,
            "mode": st.session_state["analysis_mode"],
            "keyword_limit": st.session_state["keyword_limit"],
        }

signature = st.session_state.get("analysis_signature")
stale_result = bool(
    result
    and signature
    and (
        signature["resume_text"] != resume_source_text
        or signature["job_text"] != job_source_text
        or signature["mode"] != st.session_state["analysis_mode"]
        or signature["keyword_limit"] != st.session_state["keyword_limit"]
    )
)

if stale_result:
    st.info("Inputs or scoring settings changed after the last run. Analyze again to refresh the dashboard.")

if not result:
    render_empty_state()
else:
    overview_tab, action_tab, rewrite_tab, preview_tab = st.tabs(
        ["Overview", "Action Plan", "Rewrite Lab", "Text Preview"]
    )

    with overview_tab:
        top_left, top_right = st.columns([0.95, 1.05], gap="large")

        with top_left:
            st.markdown(
                f"""
                <div class="score-card">
                    <span class="eyebrow">Overall Match</span>
                    <div class="score-value">{result['score']}%</div>
                    <p>{result['summary']}</p>
                    <div class="score-band">{result['readiness_label']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with top_right:
            st.markdown(
                f"""
                <div class="narrative-card">
                    <span class="eyebrow">{result['analysis_mode_label']}</span>
                    <h3>What to do next</h3>
                    <p>{result['next_step']}</p>
                    <div class="mini-grid">
                        <div class="mini-tile">
                            <strong>Focus area</strong>
                            <span>{result['focus_label']}</span>
                        </div>
                        <div class="mini-tile">
                            <strong>Priority terms matched</strong>
                            <span>{len(result['matched_keywords'])} of {len(result['keywords'])}</span>
                        </div>
                        <div class="mini-tile">
                            <strong>Detected sections</strong>
                            <span>{len(result['detected_sections'])} core sections found</span>
                        </div>
                        <div class="mini-tile">
                            <strong>Impact read</strong>
                            <span>{result['impact_summary']}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        meter_cols = st.columns(4, gap="large")
        meter_config = [
            ("Keyword Match", result["keyword_score"], "How closely the resume mirrors the job language.", "warm"),
            ("Impact Evidence", result["impact_score"], "How much the resume proves outcomes with numbers or scale.", "cool"),
            ("Section Coverage", result["section_score"], "How easy the resume is to scan structurally.", "navy"),
            ("Action Language", result["action_verb_score"], "How active and achievement-oriented the writing sounds.", "gold"),
        ]

        for col, config in zip(meter_cols, meter_config):
            with col:
                render_meter_card(*config)

        signal_left, signal_right = st.columns(2, gap="large")
        with signal_left:
            render_signal_stack("Strength Signals", result["strength_signals"], "positive")
        with signal_right:
            render_signal_stack("ATS / Recruiter Risks", result["ats_risks"], "warning")

        keyword_left, keyword_right = st.columns(2, gap="large")
        with keyword_left:
            st.markdown(
                """
                <div class="surface-card">
                    <span class="eyebrow">Matched Language</span>
                    <h3>What the resume already says well</h3>
                    <p>These terms already overlap with the target role and should be kept visible.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_tags(result["matched_keywords"], "good", "No meaningful keyword overlap detected yet.")

        with keyword_right:
            st.markdown(
                """
                <div class="surface-card">
                    <span class="eyebrow">Missing Language</span>
                    <h3>Priority gaps to close</h3>
                    <p>Add these only where they are truthful and supported by work, projects, or tools.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_tags(result["missing_keywords"], "warn", "No major keyword gaps detected in this pass.")

    with action_tab:
        plan_left, plan_right = st.columns([1.05, 0.95], gap="large")

        with plan_left:
            st.markdown(
                """
                <div class="surface-card">
                    <span class="eyebrow">Top Fixes</span>
                    <h3>Highest-leverage improvements first</h3>
                    <p>These are the changes most likely to improve both ATS screening and recruiter readability.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            for item in result["top_fixes"]:
                st.markdown(
                    f"""
                    <div class="list-card">
                        <div>
                            <strong>{item['title']}</strong>
                            <span>{item['detail']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with plan_right:
            st.markdown(
                """
                <div class="surface-card">
                    <span class="eyebrow">ATS Checklist</span>
                    <h3>Quick quality gates</h3>
                    <p>Use this list as a fast pass before you send the resume out.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_checklist(result["ats_checklist"])

        st.markdown(
            """
            <div class="surface-card">
                <span class="eyebrow">Section Review</span>
                <h3>How the resume reads structurally</h3>
                <p>Clear labels help both automated parsing and human scanning.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        section_cols = st.columns(2, gap="large")
        for index, item in enumerate(result["section_feedback"]):
            with section_cols[index % 2]:
                st.markdown(
                    f"""
                    <div class="list-card">
                        <div>
                            <strong>{item['section']}</strong>
                            <span>{item['feedback']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with rewrite_tab:
        rewrite_left, rewrite_right = st.columns([1.05, 0.95], gap="large")

        with rewrite_left:
            st.markdown(
                """
                <div class="surface-card">
                    <span class="eyebrow">Rewrite Ideas</span>
                    <h3>Examples you can adapt directly</h3>
                    <p>These are practical patterns, not final claims. Replace them with your own truthful details and numbers.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            for item in result["bullet_improvements"]:
                st.markdown(
                    f"""
                    <div class="list-card">
                        <div>
                            <strong>{item['issue']}</strong>
                            <span>{item['example']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with rewrite_right:
            st.markdown(
                f"""
                <div class="narrative-card">
                    <span class="eyebrow">Summary Blueprint</span>
                    <h3>Reusable positioning line</h3>
                    <p>{result['summary_template']}</p>
                    <div class="mini-grid">
                        <div class="mini-tile">
                            <strong>Role focus</strong>
                            <span>{result['focus_label']}</span>
                        </div>
                        <div class="mini-tile">
                            <strong>Keyword bridge</strong>
                            <span>{result['keyword_bridge']}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class="surface-card">
                    <span class="eyebrow">Use These Keywords</span>
                    <h3>Best terms to place in summary, skills, or top bullets</h3>
                    <p>Keep the language natural and tied to real evidence in your resume.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_tags(result["missing_keywords"][:8], "warn", "Your current resume already covers the major priority terms.")

    with preview_tab:
        if st.session_state["show_previews"]:
            preview_resume, preview_job = st.columns(2, gap="large")
            with preview_resume:
                st.markdown(
                    """
                    <div class="preview-card">
                        <span class="eyebrow">Resume Text</span>
                        <h3>Source used for analysis</h3>
                        <p>Useful for checking whether the PDF extraction preserved the content you expected.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.text_area(
                    "Resume preview",
                    value=st.session_state["resume_preview_text"],
                    height=380,
                    disabled=True,
                )

            with preview_job:
                st.markdown(
                    """
                    <div class="preview-card">
                        <span class="eyebrow">Job Description Text</span>
                        <h3>Target role content</h3>
                        <p>Review this text if the extracted keywords or scoring feel unexpectedly off.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.text_area(
                    "Job description preview",
                    value=st.session_state["job_preview_text"],
                    height=380,
                    disabled=True,
                )
        else:
            st.info("Enable 'Show extracted text previews' from the sidebar if you want to inspect the exact input used for scoring.")

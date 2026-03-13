import streamlit as st

from src.analyzer import analyze_resume


st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
)

st.title("AI Resume Analyzer")
st.caption("Compare a resume against a job description and uncover missing keywords.")

left_col, right_col = st.columns(2)

with left_col:
    resume_text = st.text_area(
        "Resume",
        height=320,
        placeholder="Paste the full resume here...",
    )

with right_col:
    job_description = st.text_area(
        "Job Description",
        height=320,
        placeholder="Paste the target job description here...",
    )

analyze_clicked = st.button("Analyze Resume", type="primary", use_container_width=True)

if analyze_clicked:
    if not resume_text.strip() or not job_description.strip():
        st.warning("Please provide both a resume and a job description.")
    else:
        result = analyze_resume(resume_text, job_description)

        score_col, matched_col, missing_col = st.columns(3)
        score_col.metric("Match Score", f"{result['score']}%")
        matched_col.metric("Matched Keywords", len(result["matched_keywords"]))
        missing_col.metric("Missing Keywords", len(result["missing_keywords"]))

        summary_left, summary_right = st.columns(2)

        with summary_left:
            st.subheader("Matched Keywords")
            if result["matched_keywords"]:
                st.write(", ".join(result["matched_keywords"]))
            else:
                st.write("No strong matches found yet.")

            st.subheader("Detected Sections")
            if result["detected_sections"]:
                st.write(", ".join(result["detected_sections"]))
            else:
                st.write("No standard resume sections detected.")

        with summary_right:
            st.subheader("Missing Keywords")
            if result["missing_keywords"]:
                st.write(", ".join(result["missing_keywords"]))
            else:
                st.write("Nice coverage. No major keyword gaps detected.")

            st.subheader("Action Verb Coverage")
            st.write(f"{result['action_verb_score']}%")

        st.subheader("Recommendations")
        for recommendation in result["recommendations"]:
            st.write(f"- {recommendation}")

        st.subheader("Section Feedback")
        for line in result["section_feedback"]:
            st.write(f"- {line}")

import json
import sqlite3
from datetime import datetime
from html import escape

import pandas as pd
import streamlit as st
from google import genai


DB_NAME = "resume_scores.db"


# -----------------------------------
# DATABASE HELPERS
# -----------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resume_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT NOT NULL,
            candidate_email TEXT,
            resume TEXT NOT NULL,
            jd TEXT NOT NULL,
            score INTEGER,
            technical_skills_match INTEGER,
            soft_skills_match INTEGER,
            experience_relevance INTEGER,
            project_fit INTEGER,
            rationale TEXT,
            missing_skills TEXT,
            suggestions TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_score(candidate_name, candidate_email, resume, jd, result):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO resume_scores (
            candidate_name,
            candidate_email,
            resume,
            jd,
            score,
            technical_skills_match,
            soft_skills_match,
            experience_relevance,
            project_fit,
            rationale,
            missing_skills,
            suggestions,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        candidate_name,
        candidate_email,
        resume,
        jd,
        result.get("score", 0),
        result.get("technical_skills_match", 0),
        result.get("soft_skills_match", 0),
        result.get("experience_relevance", 0),
        result.get("project_fit", 0),
        result.get("rationale", ""),
        json.dumps(result.get("missing_skills", [])),
        json.dumps(result.get("suggestions", [])),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def load_rankings():
    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query("""
        SELECT
            id,
            candidate_name,
            candidate_email,
            score,
            technical_skills_match,
            soft_skills_match,
            experience_relevance,
            project_fit,
            rationale,
            missing_skills,
            suggestions,
            created_at
        FROM resume_scores
        ORDER BY score DESC, created_at DESC
    """, conn)

    conn.close()
    return df


def load_candidate_result(result_id):
    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query("""
        SELECT *
        FROM resume_scores
        WHERE id = ?
    """, conn, params=(result_id,))

    conn.close()

    if df.empty:
        return None

    return df.iloc[0].to_dict()


def delete_result(result_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM resume_scores
        WHERE id = ?
    """, (result_id,))

    conn.commit()
    conn.close()


def safe_score(value):
    try:
        value = int(value)
    except Exception:
        value = 0

    return max(0, min(value, 100))


def parse_json_list(value):
    try:
        parsed = json.loads(value or "[]")
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass

    return []


def render_chips(items, css_class):
    if not items:
        return ""

    html = ""

    for item in items:
        html += f"""
        <span class="{css_class}">
            {escape(str(item))}
        </span>
        """

    return html


# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Resume AI Scorer",
    page_icon="Ã°Å¸â€œâ€ž",
    layout="wide"
)

init_db()


# -----------------------------------
# CUSTOM CSS
# -----------------------------------
st.markdown("""
<style>

:root {
    --bg-start: #f8fbff;
    --bg-end: #eef7f4;
    --surface: rgba(255, 255, 255, 0.90);
    --surface-strong: #ffffff;
    --text-main: #172033;
    --text-muted: #64748b;
    --primary: #2f80ed;
    --teal: #14b8a6;
    --primary-soft: #e8f2ff;
    --mint: #dff7ec;
    --mint-text: #10734a;
    --rose: #fff1f2;
    --rose-text: #be123c;
    --border: #dde8f2;
    --shadow: 0 16px 40px rgba(60, 72, 88, 0.10);
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes heroSweep {
    0%, 52% { transform: translateX(-110%); }
    82%, 100% { transform: translateX(110%); }
}

@keyframes gridDrift {
    from { background-position: 0 0, 0 0; }
    to { background-position: 44px 44px, 44px 44px; }
}

@keyframes floatBadge {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}

@keyframes pulseDot {
    0%, 100% { transform: scale(1); opacity: 0.75; }
    50% { transform: scale(1.45); opacity: 1; }
}

@keyframes scorePop {
    0% { transform: scale(0.94); opacity: 0.70; }
    70% { transform: scale(1.04); opacity: 1; }
    100% { transform: scale(1); }
}

@keyframes borderTrace {
    0% { opacity: 0.2; transform: translateX(-100%); }
    45%, 100% { opacity: 0.8; transform: translateX(100%); }
}

@keyframes buttonShine {
    0% { transform: translateX(-120%) skewX(-18deg); }
    48%, 100% { transform: translateX(220%) skewX(-18deg); }
}

@keyframes progressShimmer {
    from { background-position: 0 0; }
    to { background-position: 32px 0; }
}

@keyframes chipFloat {
    0% { transform: translateY(5px); opacity: 0; }
    100% { transform: translateY(0); opacity: 1; }
}

@keyframes titleLine {
    from { width: 0; }
    to { width: 86px; }
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(47,128,237,0.12), transparent 30%),
        radial-gradient(circle at top right, rgba(20,184,166,0.11), transparent 28%),
        linear-gradient(135deg, var(--bg-start), var(--bg-end));
    color: var(--text-main);
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(47,128,237,0.055) 1px, transparent 1px),
        linear-gradient(90deg, rgba(20,184,166,0.052) 1px, transparent 1px);
    background-size: 44px 44px;
    mask-image: linear-gradient(to bottom, rgba(0,0,0,0.46), transparent 72%);
    animation: gridDrift 20s linear infinite;
}

.block-container {
    padding-top: 1rem;
    max-width: 1180px;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 30px 26px;
    border: 1px solid rgba(255,255,255,0.72);
    border-radius: 18px;
    background: linear-gradient(120deg, rgba(47,128,237,0.94), rgba(20,184,166,0.88));
    color: white;
    text-align: center;
    margin-bottom: 24px;
    box-shadow: 0 18px 46px rgba(47, 128, 237, 0.16);
    animation: fadeUp 0.55s ease both;
}

.hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(110deg, transparent 15%, rgba(255,255,255,0.24) 45%, transparent 70%);
    transform: translateX(-110%);
    animation: heroSweep 5s ease-in-out infinite;
}

.hero h1,
.hero p,
.hero-badges {
    position: relative;
    z-index: 1;
}

.hero h1 {
    margin: 0;
    font-size: 40px;
    line-height: 1.1;
    letter-spacing: 0;
}

.hero p {
    margin: 9px 0 0;
    font-size: 17px;
    opacity: 0.92;
}

.hero-badges {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 18px;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.28);
    color: white;
    font-size: 13px;
    font-weight: 700;
    backdrop-filter: blur(10px);
    animation: floatBadge 3.6s ease-in-out infinite;
}

.hero-badge:nth-child(2) { animation-delay: 0.45s; }
.hero-badge:nth-child(3) { animation-delay: 0.9s; }

.pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #bbf7d0;
    box-shadow: 0 0 0 5px rgba(187,247,208,0.20);
    animation: pulseDot 1.6s ease-in-out infinite;
}

.section-title {
    margin: 24px 0 14px;
    animation: fadeUp 0.45s ease both;
}

.section-title h2 {
    margin: 0;
    font-size: 26px;
    color: var(--text-main);
    letter-spacing: 0;
}

.section-title p {
    margin: 5px 0 0;
    color: var(--text-muted);
    font-size: 14px;
}

.section-title::after {
    content: "";
    display: block;
    width: 86px;
    height: 3px;
    margin-top: 10px;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--primary), var(--teal));
    animation: titleLine 0.75s ease both;
}

.card,
.metric-card,
.score-card,
[data-testid="stDataFrame"] {
    position: relative;
    overflow: hidden;
    background: var(--surface);
    border: 1px solid rgba(221, 232, 242, 0.86);
    border-radius: 14px;
    box-shadow: var(--shadow);
    backdrop-filter: blur(14px);
    animation: fadeUp 0.5s ease both;
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.card:hover,
.metric-card:hover,
.score-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 48px rgba(60, 72, 88, 0.14);
    border-color: rgba(47,128,237,0.28);
}

.card::before,
.metric-card::before,
.score-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(47,128,237,0.56), rgba(20,184,166,0.56), transparent);
    animation: borderTrace 4.8s ease-in-out infinite;
}

.card {
    padding: 20px;
    margin-bottom: 20px;
}

.score-card {
    padding: 22px;
    margin-bottom: 18px;
    background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(232,242,255,0.9));
}

.score-card h2,
.metric-card h3 {
    margin: 0;
    color: var(--text-muted);
    font-size: 15px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0;
}

.score-card h1 {
    margin: 8px 0 0;
    color: var(--primary);
    font-size: 52px;
    line-height: 1;
    animation: scorePop 0.55s ease both;
}

.metric-card {
    padding: 18px;
    text-align: center;
}

.metric-card h2 {
    margin: 8px 0 0;
    color: var(--text-main);
    font-size: 30px;
    animation: scorePop 0.55s ease both;
}

.metric-card h3 {
    font-size: 13px;
}

.metric-card:nth-of-type(1) { animation-delay: 0.04s; }
.metric-card:nth-of-type(2) { animation-delay: 0.12s; }
.metric-card:nth-of-type(3) { animation-delay: 0.20s; }

.skill-chip,
.good-chip {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 999px;
    margin: 5px 4px;
    font-size: 14px;
    font-weight: 600;
    animation: chipFloat 0.42s ease both;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.skill-chip {
    background: var(--rose);
    color: var(--rose-text);
    border: 1px solid #ffe4e6;
}

.good-chip {
    background: var(--mint);
    color: var(--mint-text);
    border: 1px solid #bbf7d0;
}

.skill-chip:hover,
.good-chip:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(60, 72, 88, 0.12);
}

.stTextInput input,
.stTextArea textarea {
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    background: rgba(255,255,255,0.93) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: rgba(47,128,237,0.55) !important;
    box-shadow: 0 0 0 4px rgba(47,128,237,0.12) !important;
    transform: translateY(-1px);
}

.stButton button,
.stDownloadButton button {
    position: relative;
    overflow: hidden;
    border-radius: 12px !important;
    border: 0 !important;
    background: linear-gradient(90deg, #2f80ed, #14b8a6) !important;
    color: white !important;
    font-weight: 700 !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
    box-shadow: 0 10px 24px rgba(47,128,237,0.20);
}

.stButton button::after,
.stDownloadButton button::after {
    content: "";
    position: absolute;
    top: -25%;
    left: 0;
    width: 34%;
    height: 150%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.42), transparent);
    animation: buttonShine 3.8s ease-in-out infinite;
}

.stButton button:hover,
.stDownloadButton button:hover {
    transform: translateY(-2px);
    filter: brightness(1.03);
    box-shadow: 0 14px 30px rgba(20,184,166,0.24);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.72);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 8px 18px;
    transition: transform 0.18s ease, background 0.18s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    transform: translateY(-2px);
}

.stTabs [aria-selected="true"] {
    background: var(--primary-soft);
    border-color: rgba(47,128,237,0.28);
    color: var(--primary);
}

.stProgress > div > div > div > div {
    background-image:
        linear-gradient(90deg, #2f80ed, #14b8a6),
        repeating-linear-gradient(45deg, rgba(255,255,255,0.28) 0 8px, transparent 8px 16px) !important;
    background-size: 100% 100%, 32px 32px !important;
    animation: progressShimmer 1.1s linear infinite !important;
}

[data-testid="stDataFrame"] {
    border-radius: 14px;
    border: 1px solid var(--border);
}


/* -------------------------------
   RESPONSIVE LAYOUT
-------------------------------- */
@media (max-width: 900px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }

    .hero {
        padding: 24px 18px;
        margin-bottom: 18px;
        border-radius: 14px;
    }

    .hero h1 {
        font-size: 32px;
    }

    .hero p {
        font-size: 15px;
    }

    .hero-badges {
        gap: 8px;
        margin-top: 14px;
    }

    .hero-badge {
        font-size: 12px;
        padding: 7px 10px;
    }

    .section-title h2 {
        font-size: 23px;
    }

    .score-card h1 {
        font-size: 44px;
    }

    .metric-card h2 {
        font-size: 26px;
    }

    .card,
    .metric-card,
    .score-card {
        border-radius: 12px;
        padding: 16px;
    }

    .stTextArea textarea {
        min-height: 260px !important;
    }
}

@media (max-width: 640px) {
    .block-container {
        padding-top: 0.75rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }

    .hero {
        padding: 22px 14px;
        text-align: left;
    }

    .hero h1 {
        font-size: 28px;
        line-height: 1.16;
    }

    .hero p {
        font-size: 14px;
        line-height: 1.45;
    }

    .hero-badges {
        justify-content: flex-start;
    }

    .hero-badge {
        width: 100%;
        justify-content: flex-start;
    }

    .section-title {
        margin: 18px 0 12px;
    }

    .section-title h2 {
        font-size: 21px;
    }

    .section-title p {
        font-size: 13px;
        line-height: 1.45;
    }

    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto;
        flex-wrap: nowrap;
        padding-bottom: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        min-width: max-content;
        padding: 7px 14px;
    }

    .stButton button,
    .stDownloadButton button {
        min-height: 44px;
        white-space: normal;
    }

    .score-card h1 {
        font-size: 38px;
    }

    .score-card h2,
    .metric-card h3 {
        font-size: 12px;
    }

    .metric-card {
        margin-bottom: 10px;
    }

    .metric-card h2 {
        font-size: 24px;
    }

    .skill-chip,
    .good-chip {
        font-size: 13px;
        padding: 6px 10px;
        max-width: 100%;
        overflow-wrap: anywhere;
    }

    .stTextInput input {
        min-height: 42px;
    }

    .stTextArea textarea {
        min-height: 220px !important;
        font-size: 14px !important;
    }

    [data-testid="stDataFrame"] {
        overflow-x: auto;
    }

    [data-testid="stDataFrame"] div {
        font-size: 12px;
    }
}

@media (max-width: 420px) {
    .hero h1 {
        font-size: 24px;
    }

    .hero p {
        font-size: 13px;
    }

    .section-title h2 {
        font-size: 19px;
    }

    .card,
    .metric-card,
    .score-card {
        padding: 14px;
    }

    .score-card h1 {
        font-size: 34px;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.001ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: 0.001ms !important;
    }
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# HEADER
# -----------------------------------
st.markdown("""
<div class="hero">
<h1>Resume vs JD Fit Scorer</h1>
<p>AI Powered Resume Analysis and Recruiter Ranking Dashboard</p>
<div class="hero-badges">
    <span class="hero-badge"><span class="pulse-dot"></span> Live AI scoring</span>
    <span class="hero-badge"><span class="pulse-dot"></span> Ranked candidates</span>
    <span class="hero-badge"><span class="pulse-dot"></span> Skill gap insights</span>
</div>
</div>
""", unsafe_allow_html=True)


# -----------------------------------
# TABS
# -----------------------------------
tab1, tab2 = st.tabs([
    "Analyze Resume",
    "Ranked Resumes"
])


# -----------------------------------
# TAB 1: ANALYZE RESUME
# -----------------------------------
with tab1:
    st.markdown("""
    <div class="section-title">
        <h2>Candidate Details</h2>
        <p>Add the candidate profile and compare it with the selected job description.</p>
    </div>
    """, unsafe_allow_html=True)

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:
        candidate_name = st.text_input(
            "Candidate Name",
            placeholder="Enter candidate name..."
        )

    with detail_col2:
        candidate_email = st.text_input(
            "Candidate Email",
            placeholder="Enter candidate email..."
        )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Ã°Å¸â€˜Â¤ Candidate Resume")
        resume = st.text_area(
            "",
            height=420,
            placeholder="Paste Resume Here..."
        )

    with col2:
        st.markdown("### Ã°Å¸â€™Â¼ Job Description")
        jd = st.text_area(
            "",
            height=420,
            placeholder="Paste JD Here..."
        )

    api_key = st.text_input(
        "Ã°Å¸â€â€˜ Gemini API Key",
        type="password",
        placeholder="Paste Gemini API Key..."
    )

    if st.button(
        "Ã°Å¸Å¡â‚¬ Analyze Resume",
        use_container_width=True
    ):

        if not candidate_name or not resume or not jd or not api_key:
            st.warning("Please fill candidate name, resume, JD, and API key.")
            st.stop()

        try:
            with st.spinner("Analyzing Resume..."):

                client = genai.Client(
                    api_key=api_key.strip()
                )

                prompt = f"""
You are a professional recruiter.

Compare the candidate resume with the job description.

Return ONLY valid JSON using this exact structure:

{{
    "score": 0,
    "technical_skills_match": 0,
    "soft_skills_match": 0,
    "experience_relevance": 0,
    "project_fit": 0,
    "rationale": "",
    "missing_skills": [],
    "suggestions": []
}}

Scoring rules:
- score should be the overall match percentage from 0 to 100.
- technical_skills_match should be from 0 to 100.
- soft_skills_match should be from 0 to 100.
- experience_relevance should be from 0 to 100.
- project_fit should be from 0 to 100.
- missing_skills should contain important JD skills not found in the resume.
- suggestions should contain practical resume improvement suggestions.

Resume:
{resume}

Job Description:
{jd}
"""

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json"
                    }
                )

                result = json.loads(response.text)

            result["score"] = safe_score(result.get("score", 0))
            result["technical_skills_match"] = safe_score(result.get("technical_skills_match", 0))
            result["soft_skills_match"] = safe_score(result.get("soft_skills_match", 0))
            result["experience_relevance"] = safe_score(result.get("experience_relevance", 0))
            result["project_fit"] = safe_score(result.get("project_fit", 0))

            save_score(
                candidate_name=candidate_name,
                candidate_email=candidate_email,
                resume=resume,
                jd=jd,
                result=result
            )

            score = result.get("score", 0)

            st.success("Analysis saved successfully.")

            st.markdown(
                f"""
                <div class="card">
                    <h2>Ã°Å¸Å½Â¯ Overall Match Score</h2>
                    <h1 style="color:#2563eb">
                        {score}%
                    </h1>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.progress(score / 100)

            st.markdown("## Ã°Å¸â€œÅ  Match Breakdown")

            c1, c2 = st.columns(2)

            with c1:
                tech = result.get("technical_skills_match", 0)
                soft = result.get("soft_skills_match", 0)

                st.write("Technical Skills")
                st.progress(tech / 100)
                st.write(f"Match Score: {tech}%")

                st.write("Soft Skills")
                st.progress(soft / 100)
                st.write(f"Match Score: {soft}%")

            with c2:
                exp = result.get("experience_relevance", 0)
                proj = result.get("project_fit", 0)

                st.write("Experience")
                st.progress(exp / 100)
                st.write(f"Match Score: {exp}%")

                st.write("Projects")
                st.progress(proj / 100)
                st.write(f"Match Score: {proj}%")

            with st.expander(
                "Ã°Å¸â€œÂ Detailed Analysis",
                expanded=True
            ):
                st.write(
                    result.get(
                        "rationale",
                        "No analysis available."
                    )
                )

            st.markdown("## Ã¢ÂÅ’ Missing Skills")

            skills = result.get("missing_skills", [])

            if skills:
                st.markdown(
                    render_chips(skills, "skill-chip"),
                    unsafe_allow_html=True
                )
            else:
                st.success("No major skill gaps detected.")

            st.markdown("## Ã°Å¸â€™Â¡ Suggestions")

            suggestions = result.get("suggestions", [])

            if suggestions:
                for item in suggestions:
                    st.success(item)
            else:
                st.success("Resume is strongly aligned with the JD.")

        except json.JSONDecodeError:
            st.error("Gemini returned invalid JSON.")

        except Exception as e:
            st.error("Failed to analyze resume.")
            st.code(str(e))


# -----------------------------------
# TAB 2: RANKED RESUMES
# -----------------------------------
with tab2:
    st.markdown("""
    <div class="section-title">
        <h2>Ranked Resume Results</h2>
        <p>Review stored candidates by score, search, filter, and export rankings.</p>
    </div>
    """, unsafe_allow_html=True)

    rankings = load_rankings()

    if rankings.empty:
        st.info("No resumes tested yet. Analyze resumes first to build rankings.")

    else:
        total_candidates = len(rankings)
        average_score = round(rankings["score"].mean(), 2)
        top_score = int(rankings["score"].max())

        m1, m2, m3 = st.columns(3)

        with m1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h3>Total Tested</h3>
                    <h2>{total_candidates}</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

        with m2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h3>Average Score</h3>
                    <h2>{average_score}%</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

        with m3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h3>Top Score</h3>
                    <h2>{top_score}%</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("### Filters")

        filter_col1, filter_col2 = st.columns(2)

        with filter_col1:
            min_score = st.slider(
                "Minimum Score",
                0,
                100,
                0
            )

        with filter_col2:
            search_text = st.text_input(
                "Search Candidate",
                placeholder="Search by name or email..."
            )

        filtered = rankings[rankings["score"] >= min_score]

        if search_text:
            search_text = search_text.lower().strip()

            filtered = filtered[
                filtered["candidate_name"].str.lower().str.contains(search_text, na=False)
                | filtered["candidate_email"].str.lower().str.contains(search_text, na=False)
            ]

        display_df = filtered.copy()
        display_df.insert(0, "rank", range(1, len(display_df) + 1))

        display_df = display_df[[
            "rank",
            "candidate_name",
            "candidate_email",
            "score",
            "technical_skills_match",
            "soft_skills_match",
            "experience_relevance",
            "project_fit",
            "created_at"
        ]]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        csv = display_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Rankings as CSV",
            data=csv,
            file_name="resume_rankings.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("## Candidate Detail View")

        candidate_options = {
            f"{row['candidate_name']} - {row['score']}% - {row['created_at']}": row["id"]
            for _, row in filtered.iterrows()
        }

        if candidate_options:
            selected_label = st.selectbox(
                "Select Candidate Result",
                list(candidate_options.keys())
            )

            selected_id = candidate_options[selected_label]
            candidate = load_candidate_result(selected_id)

            if candidate:
                st.markdown(
                    f"""
                    <div class="card">
                        <h2>{escape(str(candidate["candidate_name"]))}</h2>
                        <p><strong>Email:</strong> {escape(str(candidate.get("candidate_email") or "Not provided"))}</p>
                        <p><strong>Score:</strong> {candidate["score"]}%</p>
                        <p><strong>Analyzed At:</strong> {candidate["created_at"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.progress(safe_score(candidate["score"]) / 100)

                d1, d2 = st.columns(2)

                with d1:
                    st.write("Technical Skills")
                    st.progress(safe_score(candidate["technical_skills_match"]) / 100)
                    st.write(f'{candidate["technical_skills_match"]}%')

                    st.write("Soft Skills")
                    st.progress(safe_score(candidate["soft_skills_match"]) / 100)
                    st.write(f'{candidate["soft_skills_match"]}%')

                with d2:
                    st.write("Experience")
                    st.progress(safe_score(candidate["experience_relevance"]) / 100)
                    st.write(f'{candidate["experience_relevance"]}%')

                    st.write("Projects")
                    st.progress(safe_score(candidate["project_fit"]) / 100)
                    st.write(f'{candidate["project_fit"]}%')

                with st.expander("Ã°Å¸â€œÂ Detailed Analysis", expanded=True):
                    st.write(candidate.get("rationale") or "No analysis available.")

                missing_skills = parse_json_list(candidate.get("missing_skills"))
                suggestions = parse_json_list(candidate.get("suggestions"))

                st.markdown("### Ã¢ÂÅ’ Missing Skills")

                if missing_skills:
                    st.markdown(
                        render_chips(missing_skills, "skill-chip"),
                        unsafe_allow_html=True
                    )
                else:
                    st.success("No major skill gaps detected.")

                st.markdown("### Ã°Å¸â€™Â¡ Suggestions")

                if suggestions:
                    for suggestion in suggestions:
                        st.success(suggestion)
                else:
                    st.success("Resume is strongly aligned with the JD.")

                with st.expander("View Stored Resume and JD"):
                    st.markdown("#### Resume")
                    st.text(candidate.get("resume") or "")

                    st.markdown("#### Job Description")
                    st.text(candidate.get("jd") or "")

                if st.button("Delete Selected Result", type="secondary"):
                    delete_result(selected_id)
                    st.success("Candidate result deleted. Refresh the page to update rankings.")
        else:
            st.info("No candidates match the current filters.")

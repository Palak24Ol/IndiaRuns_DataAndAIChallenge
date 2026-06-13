"""
Redrob AI Ranker — Streamlit Demo App
Sandbox / demo for the Redrob Data & AI Challenge submission.
Accepts a small candidate sample (≤100 candidates) and runs the full
ranking pipeline end-to-end.

Deploy to: Streamlit Cloud or HuggingFace Spaces
"""
import streamlit as st
import json
import csv
import io
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from filters import should_keep, is_honeypot
from features import extract_all_features
from scoring import coarse_score, precision_score, calibration_score, behavioral_multiplier
from reasoning import generate_reasoning

# ─── Page Config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Redrob AI Ranker",
    
    layout="wide",
)

st.title(" Redrob AI Ranker")
st.markdown("""
**Senior AI Engineer — Candidate Ranking System**

Upload a JSONL file with candidate profiles (≤100 candidates) and get a ranked Top-N output.
This is the same pipeline that processes the full 100K dataset in 7.5 seconds.
""")

st.divider()

# ─── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Pipeline Settings")
    top_n = st.slider("Top N candidates to return", 5, 100, 10)
    show_features = st.checkbox("Show feature details", value=False)
    show_raw_scores = st.checkbox("Show raw stage scores", value=True)

    st.divider()
    st.markdown("### 📊 Pipeline Architecture")
    st.markdown("""
    1. **Filter** — Title + description gates
    2. **Honeypot** — 4 detection rules
    3. **Features** — 42 features × 9 groups
    4. **Coarse** — Weighted composite
    5. **Precision** — Description-heavy rerank
    6. **Calibrate** — Top-10 ultra-specific
    7. **Reasoning** — Zero-hallucination output
    """)

# ─── File Upload ──────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    uploaded = st.file_uploader(
        "Upload candidates file",
        type=["jsonl", "json"],
        help="JSONL format (one JSON object per line) or JSON array"
    )



# ─── Load candidates ─────────────────────────────────────────────────
candidates = []

 
if uploaded:
    content = uploaded.read().decode('utf-8')
    # Try JSONL first
    lines = content.strip().split('\n')
    try:
        for line in lines:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))
    except json.JSONDecodeError:
        # Try as JSON array
        try:
            candidates = json.loads(content)
        except json.JSONDecodeError:
            st.error("Could not parse file as JSONL or JSON")

    if candidates:
        st.success(f"Loaded {len(candidates)} candidates")

# ─── Run Pipeline ─────────────────────────────────────────────────────
if candidates:
    if st.button(" Run Ranking Pipeline", type="primary"):
        with st.spinner("Running pipeline..."):
            t_start = time.time()

            # Stage 1: Filter
            survivors = [c for c in candidates if should_keep(c)]
            t_filter = time.time()

            # Stage 2: Honeypot
            for c in survivors:
                c['_honeypot'] = is_honeypot(c)
            hp_count = sum(1 for c in survivors if c['_honeypot'])

            # Stage 3: Features
            for c in survivors:
                c['_features'] = extract_all_features(c)

            # Stage 4: Coarse
            for c in survivors:
                c['_coarse'] = coarse_score(c['_features'], c['_honeypot'])
            survivors.sort(key=lambda c: (-c['_coarse'], c['candidate_id']))
            top_200 = survivors[:200]

            # Stage 5: Precision
            for c in top_200:
                c['_precision'] = precision_score(c['_features'])
            top_200.sort(key=lambda c: (-c['_precision'], c['candidate_id']))
            top_100 = top_200[:100]

            # Stage 6: Calibration
            top_20 = top_100[:20]
            rest = top_100[20:]
            for c in top_20:
                c['_calibration'] = calibration_score(c, c['_features'])
            top_20.sort(key=lambda c: (-c['_calibration'], c['candidate_id']))
            final = (top_20 + rest)[:top_n]

            t_end = time.time()

        # ─── Results ──────────────────────────────────────────────────
        st.divider()

        # Metrics row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Input", f"{len(candidates):,}")
        m2.metric("Survivors", f"{len(survivors):,}")
        m3.metric("Honeypots", f"{hp_count}")
        m4.metric("Runtime", f"{t_end - t_start:.2f}s")

        st.divider()

        # Results table
        st.subheader(f"🏆 Top {len(final)} Ranked Candidates")

        rows = []
        for rank_idx, c in enumerate(final):
            rank = rank_idx + 1
            score = round(1.0 - (rank - 1) * (0.99 / max(len(final) - 1, 1)), 4)
            reason = generate_reasoning(c, c['_features'])
            p = c['profile']
            f = c['_features']

            row = {
                'Rank': rank,
                'Candidate ID': c['candidate_id'],
                'Title': p['current_title'],
                'Company': p['current_company'],
                'YOE': f"{p['years_of_experience']:.1f}",
                'Location': f"{p['location']} ({p['country']})",
                'Score': f"{score:.4f}",
            }

            if show_raw_scores:
                row['Coarse'] = f"{c.get('_coarse', 0):.4f}"
                row['Precision'] = f"{c.get('_precision', 0):.4f}"
                if '_calibration' in c:
                    row['Calibration'] = f"{c['_calibration']:.4f}"

            row['Reasoning'] = reason[:200] + '...' if len(reason) > 200 else reason
            rows.append(row)

        st.dataframe(rows, use_container_width=True, hide_index=True)

        # Feature details expander
        if show_features and final:
            st.subheader("📋 Feature Details")
            for rank_idx, c in enumerate(final[:5]):
                with st.expander(f"#{rank_idx + 1} — {c['profile']['current_title']} at {c['profile']['current_company']}"):
                    f = c['_features']
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.markdown("**Group A: Title & Role**")
                        st.write(f"A1 title_relevance: {f['A1']:.2f}")
                        st.write(f"A2 career_ai_ratio: {f['A2']:.2f}")
                        st.write(f"A3 retrieval_ratio: {f['A3']:.2f}")
                        st.markdown("**Group B: Descriptions**")
                        st.write(f"B1 retrieval_kw: {f['B1']:.2f} (raw={f['_retrieval_raw']:.0f})")
                        st.write(f"B2 production_kw: {f['B2']:.2f} (raw={f['_production_raw']:.0f})")
                        st.write(f"B3 ml_kw: {f['B3']:.2f} (raw={f['_ml_raw']:.0f})")
                    with col_b:
                        st.markdown("**Group C: Skill Depth**")
                        st.write(f"C1 retrieval_skill: {f['C1']:.2f}")
                        st.write(f"C2 nice_to_have: {f['C2']:.2f}")
                        st.write(f"C4 expert_count: {f['C4']:.2f}")
                        st.markdown("**Group D: Experience**")
                        st.write(f"D1 yoe_fit: {f['D1']:.2f}")
                        st.write(f"D2 ai_months: {f['D2']:.2f}")
                    with col_c:
                        st.markdown("**Group H: Behavioral**")
                        st.write(f"H1 recency: {f['H1']:.2f}")
                        st.write(f"H2 response_rate: {f['H2']:.2f}")
                        st.write(f"H8 saved_by_recruiter: {f['H8']:.2f}")
                        bm = behavioral_multiplier(f)
                        st.write(f"**Behavioral mult: {bm:.4f}**")

        # Download CSV
        st.divider()
        csv_buf = io.StringIO()
        writer = csv.writer(csv_buf)
        writer.writerow(['candidate_id', 'rank', 'score', 'reasoning'])
        for rank_idx, c in enumerate(final):
            rank = rank_idx + 1
            score = round(1.0 - (rank - 1) * (0.99 / max(len(final) - 1, 1)), 4)
            reason = generate_reasoning(c, c['_features'])
            writer.writerow([c['candidate_id'], rank, f'{score:.4f}', reason])

        st.download_button(
            "📥 Download Ranked CSV",
            csv_buf.getvalue(),
            "submission.csv",
            "text/csv",
            type="primary",
        )

else:
    st.info("👆 Upload a candidates file and wait")

# ─── Footer ──────────────────────────────────────────────────────────
st.divider()
st.caption("Redrob Data & AI Challenge — 3-Stage Retrieval & Ranking Pipeline | 42 Features | 7.5s Runtime | Zero Dependencies")

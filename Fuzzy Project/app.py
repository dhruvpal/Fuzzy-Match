"""
Universal Fuzzy Data Matcher — Streamlit App with Lovable UI
============================================================
Seamlessly combines the Lovable dark-indigo SaaS design system with the
robust, domain-agnostic Python RapidFuzz matching engine.
"""

import os
import sys
import json
import datetime
import streamlit as st
import pandas as pd
from typing import List, Dict, Any

from file_loader import (
    load_sample_dataset,
    load_and_combine_master_datasets
)
from matcher import (
    MatchingRule,
    run_fuzzy_matching
)
from utils import (
    export_dataframe_to_excel_bytes,
    export_dataframe_to_csv_bytes
)
from ui_templates import (
    get_css_bundle,
    render_top_banner,
    render_card_header,
    render_stepper,
    render_kpi_cards,
    render_donut_chart,
    render_confidence_barchart,
    render_file_card,
    render_weight_bar
)

# Page configuration
st.set_page_config(
    page_title="Universal Match AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Lovable CSS bundle
st.html(get_css_bundle())


# -------------------------------------------------------------
# Session State Initialization
# -------------------------------------------------------------
def init_session():
    if 'nav_page' not in st.session_state:
        st.session_state.nav_page = "Dashboard"
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'sample_df' not in st.session_state:
        st.session_state.sample_df = None
    if 'sample_meta' not in st.session_state:
        st.session_state.sample_meta = None
    if 'master_df' not in st.session_state:
        st.session_state.master_df = None
    if 'master_meta' not in st.session_state:
        st.session_state.master_meta = None
    if 'results_df' not in st.session_state:
        st.session_state.results_df = None
    if 'summary_stats' not in st.session_state:
        st.session_state.summary_stats = None
    if 'match_history' not in st.session_state:
        st.session_state.match_history = []
    if 'num_rules' not in st.session_state:
        st.session_state.num_rules = 2
    if 'high_threshold' not in st.session_state:
        st.session_state.high_threshold = 90
    if 'review_threshold' not in st.session_state:
        st.session_state.review_threshold = 75


init_session()


# -------------------------------------------------------------
# Sidebar: Brand, Navigation & Settings
# -------------------------------------------------------------
with st.sidebar:
    st.html("""
    <div style="display:flex;align-items:center;gap:12px;padding:8px 0 16px;border-bottom:1px solid rgba(140,165,235,0.14);margin-bottom:16px;">
        <div style="width:38px;height:38px;border-radius:11px;background:linear-gradient(135deg,#4f7cff,#7c5cff);display:grid;place-items:center;box-shadow:0 0 12px rgba(79,124,255,0.5);">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><path d="M3 7h6l2 5 2-10 2 5h4"/></svg>
        </div>
        <div>
            <div style="font-weight:800;font-size:16px;color:#fff;letter-spacing:-0.02em;">Universal Match AI</div>
            <div style="font-size:11px;color:#7683a6;">Enterprise Data Workspace</div>
        </div>
    </div>
    """)

    st.caption("WORKSPACE")
    nav_options = ["Dashboard", "New Match", "Review Center", "Match History", "Settings"]
    selected_nav = st.radio(
        "Navigation",
        options=nav_options,
        index=nav_options.index(st.session_state.nav_page),
        label_visibility="collapsed"
    )
    if selected_nav != st.session_state.nav_page:
        st.session_state.nav_page = selected_nav
        st.rerun()

    st.markdown("---")
    st.caption("ENGINE SETTINGS")
    st.session_state.high_threshold = st.slider(
        "High Confidence (≥)",
        min_value=50, max_value=100, value=int(st.session_state.high_threshold), step=1,
        help="Matches at or above this score are auto-accepted."
    )
    st.session_state.review_threshold = st.slider(
        "Review Required (≥)",
        min_value=30, max_value=90, value=int(st.session_state.review_threshold), step=1,
        help="Matches between Review Threshold and High Confidence are flagged for review."
    )

    st.markdown("---")
    st.caption("QUICK ACTIONS")
    if st.button("⚡ Load Demo Files (Current Data)", use_container_width=True):
        sample_path = "Response Data (161).csv"
        master_paths = ["1-27jun.csv", "5 - 15 aug.csv", "20 - 05 aug.csv", "28-20july.csv"]
        missing = [p for p in [sample_path] + master_paths if not os.path.exists(p)]
        if missing:
            st.error(f"Missing files: {', '.join(missing)}")
        else:
            with st.spinner("Loading demo files..."):
                s_df, s_meta = load_sample_dataset(sample_path)
                m_df, m_meta = load_and_combine_master_datasets(master_paths)
                st.session_state.sample_df = s_df
                st.session_state.sample_meta = s_meta
                st.session_state.master_df = m_df
                st.session_state.master_meta = m_meta
                st.session_state.current_step = 2
                st.session_state.nav_page = "New Match"
                st.toast("Loaded 161 sample records + 62,580 master records!", icon="✅")
                st.rerun()

    if st.button("🗑️ Reset Workspace", use_container_width=True):
        st.session_state.sample_df = None
        st.session_state.sample_meta = None
        st.session_state.master_df = None
        st.session_state.master_meta = None
        st.session_state.results_df = None
        st.session_state.summary_stats = None
        st.session_state.current_step = 1
        st.rerun()


# Helper function to compute confidence distribution
def compute_conf_distribution(df_res: Optional[pd.DataFrame]) -> List[Dict[str, Any]]:
    if df_res is None or len(df_res) == 0:
        return [
            {'label': '< 50', 'value': 0, 'tone': 'danger'},
            {'label': '50–59', 'value': 0, 'tone': 'danger'},
            {'label': '60–69', 'value': 0, 'tone': 'warning'},
            {'label': '70–79', 'value': 0, 'tone': 'warning'},
            {'label': '80–89', 'value': 0, 'tone': 'success'},
            {'label': '90–100', 'value': 0, 'tone': 'success'}
        ]
    scores = df_res['Final Score']
    return [
        {'label': '< 50', 'value': int((scores < 50).sum()), 'tone': 'danger'},
        {'label': '50–59', 'value': int(((scores >= 50) & (scores < 60)).sum()), 'tone': 'danger'},
        {'label': '60–69', 'value': int(((scores >= 60) & (scores < 70)).sum()), 'tone': 'warning'},
        {'label': '70–79', 'value': int(((scores >= 70) & (scores < 80)).sum()), 'tone': 'warning'},
        {'label': '80–89', 'value': int(((scores >= 80) & (scores < 90)).sum()), 'tone': 'success'},
        {'label': '90–100', 'value': int((scores >= 90).sum()), 'tone': 'success'}
    ]


# =============================================================
# VIEW 1: DASHBOARD
# =============================================================
if st.session_state.nav_page == "Dashboard":
    st.html(render_top_banner("Dashboard", "Find the right record from messy data."))

    summary = st.session_state.summary_stats or {
        'total_samples': 0,
        'high_confidence': 0,
        'review': 0,
        'no_match': 0,
        'match_rate': 0.0
    }

    # 4 KPI Cards
    st.html(render_kpi_cards(
        total=summary['total_samples'],
        matched=summary['high_confidence'],
        review=summary['review'],
        no_match=summary['no_match'],
        match_rate=summary['match_rate']
    ))

    # Charts Grid
    col_chart1, col_chart2 = st.columns([1.6, 1.0])

    with col_chart1:
        st.html(render_card_header("Match Quality & Confidence Distribution", "Score distribution bucketed by confidence bands"))
        dist_data = compute_conf_distribution(st.session_state.results_df)
        st.html(render_confidence_barchart(dist_data))

    with col_chart2:
        st.html(render_card_header("Match Rate", "Auto-accepted at ≥ 90% confidence"))
        st.html(render_donut_chart(summary['match_rate'], "Resolved", 130))

    # Recent Jobs / Quick Action
    st.html(render_card_header("Recent Matching Jobs", "History of batch executions in this workspace"))

    if st.session_state.match_history:
        history_df = pd.DataFrame(st.session_state.match_history)
        st.dataframe(history_df, use_container_width=True)
    else:
        st.caption("No previous jobs in this session yet. Click below to start matching.")

    if st.button("🚀 Start a New Match Job", type="primary", use_container_width=True):
        st.session_state.nav_page = "New Match"
        st.session_state.current_step = 1
        st.rerun()


# =============================================================
# VIEW 2: NEW MATCH (4 STEPS)
# =============================================================
elif st.session_state.nav_page == "New Match":
    st.html(render_top_banner("New Match", "Upload, configure, run and review in four steps."))

    # Render Stepper
    st.html(render_stepper(st.session_state.current_step))

    # ---------------------------------------------------------
    # STEP 1: UPLOAD DATA
    # ---------------------------------------------------------
    if st.session_state.current_step == 1:
        u_col1, u_col2 = st.columns(2)

        with u_col1:
            st.html(render_card_header("Reference / Sample Data", "The messy records you want to resolve", "Required", "info"))

            up_sample = st.file_uploader(
                "Upload Reference File (CSV / Excel)",
                type=['csv', 'xlsx', 'xls'],
                key="step1_sample_uploader"
            )
            if up_sample is not None:
                try:
                    s_df, s_meta = load_sample_dataset(up_sample)
                    st.session_state.sample_df = s_df
                    st.session_state.sample_meta = s_meta
                except Exception as e:
                    st.error(f"Error loading file: {e}")

            if st.session_state.sample_meta:
                meta = st.session_state.sample_meta
                st.html(render_file_card(meta['filename'], meta['rows'], meta['columns_count']))
                with st.expander("Preview Sample (First 5 Rows)"):
                    st.dataframe(st.session_state.sample_df.head(5), use_container_width=True)

        with u_col2:
            st.html(render_card_header("Master Data", "Trusted source of truth to match against", "Multiple Allowed", "neutral"))

            up_masters = st.file_uploader(
                "Upload Master Files (CSV / Excel)",
                type=['csv', 'xlsx', 'xls'],
                accept_multiple_files=True,
                key="step1_master_uploader"
            )
            if up_masters:
                try:
                    m_df, m_meta = load_and_combine_master_datasets(up_masters)
                    st.session_state.master_df = m_df
                    st.session_state.master_meta = m_meta
                except Exception as e:
                    st.error(f"Error loading master files: {e}")

            if st.session_state.master_meta:
                m_meta = st.session_state.master_meta
                for f_info in m_meta['file_details']:
                    st.html(render_file_card(f_info['filename'], f_info['rows'], f_info['columns_count'], is_master=True))
                st.caption(f"**Total Combined Master Records:** {m_meta['total_rows']:,}")
                with st.expander("Preview Master (First 5 Rows)"):
                    st.dataframe(st.session_state.master_df.head(5), use_container_width=True)

        # Action bar
        can_proceed_step1 = (st.session_state.sample_df is not None) and (st.session_state.master_df is not None)
        st.markdown("<br>", unsafe_allow_html=True)
        _, act_col = st.columns([4, 1.5])
        with act_col:
            if st.button("Continue to Configuration ➔", type="primary", disabled=not can_proceed_step1, use_container_width=True):
                st.session_state.current_step = 2
                st.rerun()

    # ---------------------------------------------------------
    # STEP 2: CONFIGURE MATCHING
    # ---------------------------------------------------------
    elif st.session_state.current_step == 2:
        if st.session_state.sample_df is None or st.session_state.master_df is None:
            st.warning("Please upload reference and master datasets first.")
            if st.button("⬅️ Back to Upload"):
                st.session_state.current_step = 1
                st.rerun()
        else:
            sample_cols = list(st.session_state.sample_df.columns)
            master_cols = [c for c in st.session_state.master_df.columns if c != "Source Master File"]

            st.html(render_card_header("Column Mapping Rules", "Pair reference columns with master columns and assign their relative weights"))

            ctrl_c1, ctrl_c2, _ = st.columns([1, 1, 4])
            with ctrl_c1:
                if st.button("➕ Add Rule"):
                    st.session_state.num_rules += 1
                    st.rerun()
            with ctrl_c2:
                if st.button("➖ Remove Rule") and st.session_state.num_rules > 1:
                    st.session_state.num_rules -= 1
                    st.rerun()

            rules_list: List[MatchingRule] = []
            rules_ui_data = []
            total_weight = 0.0

            for r_i in range(st.session_state.num_rules):
                rc1, rc2, rc3, rc4 = st.columns([3, 3.5, 2, 1.8])
                with rc1:
                    s_idx = min(r_i, len(sample_cols) - 1)
                    s_col = st.selectbox(f"Reference Column #{r_i+1}", options=sample_cols, index=s_idx, key=f"s_col_{r_i}")
                with rc2:
                    m_idx = min(r_i, len(master_cols) - 1)
                    m_cols = st.multiselect(
                        f"Master Target Column(s) #{r_i+1}",
                        options=master_cols,
                        default=[master_cols[m_idx]],
                        key=f"m_cols_{r_i}",
                        help="Select one or multiple master fields (e.g. Category + Full Name)."
                    )
                with rc3:
                    default_wt = 60 if r_i == 0 else (40 if r_i == 1 else 0)
                    if st.session_state.num_rules == 1:
                        default_wt = 100
                    wt = st.slider(f"Weight % #{r_i+1}", min_value=0, max_value=100, value=int(default_wt), step=5, key=f"wt_{r_i}")
                    total_weight += wt
                with rc4:
                    mode = st.selectbox(f"Mode #{r_i+1}", options=["Automatic", "Text Fuzzy", "Exact", "Numeric", "Date"], index=0, key=f"mode_{r_i}")

                if s_col and m_cols and wt > 0:
                    rules_list.append(MatchingRule(
                        sample_col=s_col,
                        master_col=m_cols,
                        weight=wt,
                        mode=mode.lower().replace(" ", "_")
                    ))
                    rules_ui_data.append({'name': s_col, 'weight': wt})

            # Weightbar & indicator
            st.html(render_weight_bar(rules_ui_data))

            if total_weight == 100:
                st.success(f"✅ Total Weight: **{total_weight:.0f}%** (Valid)")
            else:
                st.error(f"❌ Total Weight must equal **100%**. Current: **{total_weight:.0f}%**")

            # Return Columns Card
            st.html(render_card_header("Return Columns", "Select which master columns to include in the output results"))

            suggested = [c for c in master_cols if any(k in c.lower() for k in ['code', 'id', 'sku', 'ref', 'name', 'model'])]
            default_ret = suggested[:2] if suggested else master_cols[:1]

            selected_return_cols = st.multiselect(
                "Master Columns to Return:",
                options=master_cols,
                default=default_ret,
                key="step2_return_cols"
            )

            # Action bar
            can_run = (total_weight == 100) and (len(rules_list) > 0) and (len(selected_return_cols) > 0)
            st.markdown("<br>", unsafe_allow_html=True)
            act1, _, act2 = st.columns([1.5, 3, 2])
            with act1:
                if st.button("⬅️ Back to Upload", use_container_width=True):
                    st.session_state.current_step = 1
                    st.rerun()
            with act2:
                if st.button("🚀 Run Fuzzy Matching", type="primary", disabled=not can_run, use_container_width=True):
                    st.session_state.active_rules = rules_list
                    st.session_state.selected_return_cols = selected_return_cols
                    st.session_state.current_step = 3
                    st.rerun()

    # ---------------------------------------------------------
    # STEP 3: RUN MATCHING (PROCESSING)
    # ---------------------------------------------------------
    elif st.session_state.current_step == 3:
        st.html(render_card_header("Matching in Progress", "RapidFuzz engine is evaluating candidates and calculating weighted similarity", "Processing", "info"))

        prog_bar = st.progress(0.0)
        status_msg = st.empty()

        def on_progress(p, msg):
            prog_bar.progress(p)
            status_msg.markdown(f"**Status:** *{msg}*")

        try:
            res_df, summary = run_fuzzy_matching(
                df_sample=st.session_state.sample_df,
                df_master=st.session_state.master_df,
                rules=st.session_state.active_rules,
                return_cols=st.session_state.selected_return_cols,
                high_threshold=float(st.session_state.high_threshold),
                review_threshold=float(st.session_state.review_threshold),
                progress_callback=on_progress
            )
            st.session_state.results_df = res_df
            st.session_state.summary_stats = summary

            # Add to history
            st.session_state.match_history.insert(0, {
                'Job': f"Job #{len(st.session_state.match_history)+1}",
                'Reference File': st.session_state.sample_meta['filename'],
                'Rows': summary['total_samples'],
                'Match Rate': f"{summary['match_rate']}%",
                'High Conf': summary['high_confidence'],
                'Review': summary['review'],
                'Created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })

            st.session_state.current_step = 4
            st.rerun()
        except Exception as e:
            st.error(f"Execution Error: {e}")
            if st.button("⬅️ Back to Configuration"):
                st.session_state.current_step = 2
                st.rerun()

    # ---------------------------------------------------------
    # STEP 4: RESULTS DASHBOARD
    # ---------------------------------------------------------
    elif st.session_state.current_step == 4:
        if st.session_state.results_df is None:
            st.warning("No results available. Please run matching first.")
            if st.button("⬅️ Go to Step 1"):
                st.session_state.current_step = 1
                st.rerun()
        else:
            res_df = st.session_state.results_df
            summary = st.session_state.summary_stats

            # KPI Cards
            st.html(render_kpi_cards(
                total=summary['total_samples'],
                matched=summary['high_confidence'],
                review=summary['review'],
                no_match=summary['no_match'],
                match_rate=summary['match_rate']
            ))

            # Visual Charts Grid
            c_r1, c_r2 = st.columns([1, 1.5])
            with c_r1:
                st.html(render_card_header("Match Rate", "Share of records resolved"))
                st.html(render_donut_chart(summary['match_rate'], "Resolved", 130))
                st.caption(f"**{summary['high_confidence']}** of **{summary['total_samples']}** auto-accepted.")

            with c_r2:
                st.html(render_card_header("Confidence Distribution", "Scores bucketed in 10-point bands"))
                dist_data = compute_conf_distribution(res_df)
                st.html(render_confidence_barchart(dist_data))

            # Results Table Card with Search & Filters
            st.html(render_card_header("Match Results Table", "Search, filter, inspect details, and export datasets"))

            # Filter controls
            tf1, tf2, tf3 = st.columns([2, 2, 4])
            with tf1:
                s_filter = st.selectbox("Status Filter:", ["ALL", "HIGH CONFIDENCE", "REVIEW", "NO MATCH"], index=0)
            with tf2:
                min_score = st.slider("Min Final Score:", 0, 100, 0, 5)
            with tf3:
                q = st.text_input("🔍 Search table text:", placeholder="Search by name, product, code...")

            filtered_df = res_df.copy()
            if s_filter != "ALL":
                filtered_df = filtered_df[filtered_df['Match Status'] == s_filter]
            if min_score > 0:
                filtered_df = filtered_df[filtered_df['Final Score'] >= min_score]
            if q:
                query_str = q.lower()
                mask = filtered_df.astype(str).apply(lambda row: query_str in row.str.lower().values, axis=1)
                filtered_df = filtered_df[mask]

            display_cols = [c for c in filtered_df.columns if not c.startswith('_')]
            st.dataframe(filtered_df[display_cols], use_container_width=True, height=420)
            st.caption(f"Showing **{len(filtered_df):,}** of **{len(res_df):,}** records.")

            # Match Detail Drawer / Inspector
            st.html(render_card_header("Inspect Record Detail & Alternative Candidates", "Select any sample row to view score breakdowns and top alternative matches"))

            row_options = list(range(1, len(res_df) + 1))
            selected_row_num = st.selectbox("Select Sample Row # to inspect:", options=row_options, index=0)

            if selected_row_num:
                row_data = res_df.iloc[selected_row_num - 1]
                stat_badge = "uma-badge--high" if row_data['Match Status'] == 'HIGH CONFIDENCE' else ("uma-badge--review" if row_data['Match Status'] == 'REVIEW' else "uma-badge--none")

                st.html(f"""
                <div class="uma-compare-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <span class="uma-badge {stat_badge}"><span class="dot"></span>{row_data['Match Status']}</span>
                            <span class="uma-mono" style="margin-left:10px;font-size:14px;color:#fff;">Final Score: <b>{row_data['Final Score']}%</b></span>
                        </div>
                        <span class="uma-muted" style="font-size:12px;">Source: {row_data.get('Source Master File', '')}</span>
                    </div>
                </div>
                """)

                dt_c1, dt_c2 = st.columns(2)
                with dt_c1:
                    st.caption("**Reference Input:**")
                    for c in res_df.columns:
                        if c.startswith('Sample:'):
                            st.write(f"- **{c.replace('Sample: ', '')}**: `{row_data[c]}`")
                    st.caption(f"Explanation: *{row_data.get('Explanation', '')}*")

                with dt_c2:
                    st.caption("**Matched Master Record:**")
                    for c in res_df.columns:
                        if c.startswith('Matched:'):
                            st.write(f"- **{c.replace('Matched: ', '')}**: `{row_data[c]}`")
                    for ret in st.session_state.selected_return_cols:
                        st.write(f"- **{ret}**: `{row_data.get(ret, '')}`")

                # Show Alternative Candidates
                alts = row_data.get('_alternative_candidates', [])
                if alts:
                    st.caption("TOP ALTERNATIVE CANDIDATES EVALUATED:")
                    alt_table = []
                    for c_num, cand in enumerate(alts, 1):
                        entry = {'Candidate': f"#{c_num}", 'Score': f"{cand['Score']}%", 'Source': cand['Source']}
                        entry.update(cand['Values'])
                        alt_table.append(entry)
                    st.table(pd.DataFrame(alt_table))

            # Export Hub
            st.html(render_card_header("Download Results", "Export results in formatted Excel (.xlsx) workbooks or UTF-8 CSV"))

            clean_df = res_df[[c for c in res_df.columns if not c.startswith('_')]].copy()
            high_df = clean_df[clean_df['Match Status'] == 'HIGH CONFIDENCE'].copy()
            rev_df = clean_df[clean_df['Match Status'] == 'REVIEW'].copy()
            none_df = clean_df[clean_df['Match Status'] == 'NO MATCH'].copy()

            d1, d2, d3, d4 = st.columns(4)
            with d1:
                st.markdown("**📦 All Results**")
                st.download_button("Excel (.xlsx)", data=export_dataframe_to_excel_bytes(clean_df, "All"), file_name="fuzzy_match_results.xlsx", use_container_width=True)
                st.download_button("CSV (.csv)", data=export_dataframe_to_csv_bytes(clean_df), file_name="fuzzy_match_results.csv", use_container_width=True)
            with d2:
                st.markdown("**🌟 High Confidence**")
                st.download_button("Excel (.xlsx)", data=export_dataframe_to_excel_bytes(high_df, "High"), file_name="high_confidence_matches.xlsx", disabled=len(high_df)==0, use_container_width=True)
                st.download_button("CSV (.csv)", data=export_dataframe_to_csv_bytes(high_df), file_name="high_confidence_matches.csv", disabled=len(high_df)==0, use_container_width=True)
            with d3:
                st.markdown("**⚠️ Review Required**")
                st.download_button("Excel (.xlsx)", data=export_dataframe_to_excel_bytes(rev_df, "Review"), file_name="review_required.xlsx", disabled=len(rev_df)==0, use_container_width=True)
                st.download_button("CSV (.csv)", data=export_dataframe_to_csv_bytes(rev_df), file_name="review_required.csv", disabled=len(rev_df)==0, use_container_width=True)
            with d4:
                st.markdown("**❌ No Match**")
                st.download_button("Excel (.xlsx)", data=export_dataframe_to_excel_bytes(none_df, "NoMatch"), file_name="no_match.xlsx", disabled=len(none_df)==0, use_container_width=True)
                st.download_button("CSV (.csv)", data=export_dataframe_to_csv_bytes(none_df), file_name="no_match.csv", disabled=len(none_df)==0, use_container_width=True)


# =============================================================
# VIEW 3: REVIEW CENTER
# =============================================================
elif st.session_state.nav_page == "Review Center":
    st.html(render_top_banner("Review Center", "Resolve uncertain matches with full context and alternative candidates."))

    if st.session_state.results_df is None:
        st.info("No matching job has been executed yet. Run a match first.")
    else:
        res_df = st.session_state.results_df
        review_records = res_df[res_df['Match Status'].isin(['REVIEW', 'NO MATCH'])].copy()

        if len(review_records) == 0:
            st.success("🎉 All records were matched with High Confidence! No review is needed.")
        else:
            st.markdown(f"**Found {len(review_records)} uncertain records requiring human review:**")

            for idx, r_row in review_records.iterrows():
                r_num = r_row['Sample Row #']
                status = r_row['Match Status']
                badge_cls = "uma-badge--review" if status == "REVIEW" else "uma-badge--none"

                with st.expander(f"Row #{r_num} | {status} (Score: {r_row['Final Score']}%) | {r_row.get(list(r_row.keys())[1], '')}", expanded=False):
                    rc_1, rc_2 = st.columns(2)
                    with rc_1:
                        st.markdown("**Reference Query Input:**")
                        for col in res_df.columns:
                            if col.startswith('Sample:'):
                                st.write(f"- **{col.replace('Sample: ', '')}**: `{r_row[col]}`")
                        st.caption(f"Explanation: *{r_row.get('Explanation', '')}*")

                    with rc_2:
                        st.markdown("**Best Match Found:**")
                        for col in res_df.columns:
                            if col.startswith('Matched:'):
                                st.write(f"- **{col.replace('Matched: ', '')}**: `{r_row[col]}`")
                        st.write(f"- **Source File**: `{r_row.get('Source Master File', '')}`")

                    # Alternative Candidates Table
                    alts = r_row.get('_alternative_candidates', [])
                    if alts:
                        st.markdown("**Alternative Candidates:**")
                        alt_list = []
                        for c_i, c_obj in enumerate(alts, 1):
                            d = {'#': f"Candidate {c_i}", 'Score': f"{c_obj['Score']}%", 'File': c_obj['Source']}
                            d.update(c_obj['Values'])
                            alt_list.append(d)
                        st.table(pd.DataFrame(alt_list))


# =============================================================
# VIEW 4: MATCH HISTORY
# =============================================================
elif st.session_state.nav_page == "Match History":
    st.html(render_top_banner("Match History", "All matching jobs executed in this session."))

    if st.session_state.match_history:
        st.dataframe(pd.DataFrame(st.session_state.match_history), use_container_width=True)
    else:
        st.caption("No jobs executed in this session yet.")


# =============================================================
# VIEW 5: SETTINGS
# =============================================================
elif st.session_state.nav_page == "Settings":
    st.html(render_top_banner("Settings", "Defaults for engine, thresholds and exports."))

    s_col1, s_col2 = st.columns(2)
    with s_col1:
        st.html(render_card_header("Matching Engine Defaults", "Algorithms and normalizers"))
        st.selectbox("Default String Scorer", ["RapidFuzz — token_sort_ratio", "RapidFuzz — token_set_ratio", "RapidFuzz — WRatio"], index=0)
        st.checkbox("Normalize whitespace and strip punctuation", value=True)
        st.checkbox("Case-insensitive matching", value=True)

    with s_col2:
        st.html(render_card_header("Export Defaults", "Default format and retention"))
        st.selectbox("Default Export Type", ["Excel (.xlsx)", "CSV (.csv)", "Both"], index=0)
        st.text_input("Workspace Name", value="Universal Match AI")

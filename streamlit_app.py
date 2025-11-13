# streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
import os
from math import pi
import matplotlib.pyplot as plt

# -------------------------
# INDUSTRY STANDARD WEIGHTS
# -------------------------
STANDARD_WEIGHTS = {
    "Technology": 0.25,
    "Process": 0.20,
    "People": 0.20,
    "Data": 0.15,
    "Strategy": 0.20
}

# -------------------------
# DROPDOWN OPTIONS (mapped to 1–5)
# -------------------------
TECH_OPTIONS = [
    ("No sensors, manual data entry",1),
    ("Basic sensors on critical machines",2),
    ("Machines connected locally (PLC)",3),
    ("Real-time monitoring & dashboards",4),
    ("Predictive maintenance & IoT-enabled",5)
]
PROCESS_OPTIONS = [
    ("Ad-hoc / manual processes",1),
    ("Standard documented processes",2),
    ("Partial digital integration (ERP/MES-lite)",3),
    ("Integrated planning & MES",4),
    ("Autonomous scheduling / flexible cells",5)
]
PEOPLE_OPTIONS = [
    ("No digital skills",1),
    ("Basic digital literacy",2),
    ("Operators trained for automation",3),
    ("Data-savvy workforce",4),
    ("Cross-functional digital culture",5)
]
DATA_OPTIONS = [
    ("No digital data / paper only",1),
    ("Local digital logs",2),
    ("Real-time data capture",3),
    ("Analytics & dashboards",4),
    ("AI-driven decision making",5)
]
STRATEGY_OPTIONS = [
    ("No digital roadmap",1),
    ("Ad-hoc projects",2),
    ("Defined digital goals",3),
    ("Budgeted transformation plan",4),
    ("Continuous innovation strategy",5)
]

# -------------------------
# PAGE SETUP
# -------------------------
st.set_page_config(page_title="I4MM Advanced CNC", layout="wide")
st.title("🏭 I4MM Advanced — CNC Machining & Assembly Cell")

st.markdown("<hr>", unsafe_allow_html=True)

# -------------------------
# SIDEBAR PARAMETERS
# -------------------------
st.sidebar.header("⚙️ Input Parameters (sticky)")

system = st.sidebar.selectbox("Select System", ["CNC Machining & Assembly Cell"])
use_standard_weights = st.sidebar.checkbox("Use standard weights (industry-aligned)", value=True)

st.sidebar.markdown("### Weight Distribution")
if use_standard_weights:
    for k,v in STANDARD_WEIGHTS.items():
        st.sidebar.write(f"{k}: {v:.2f}")
else:
    w_tech = st.sidebar.slider("Technology", 0.0, 1.0, 0.25, 0.05)
    w_proc = st.sidebar.slider("Process", 0.0, 1.0, 0.20, 0.05)
    w_people = st.sidebar.slider("People", 0.0, 1.0, 0.20, 0.05)
    w_data = st.sidebar.slider("Data", 0.0, 1.0, 0.15, 0.05)
    w_strat = st.sidebar.slider("Strategy", 0.0, 1.0, 0.20, 0.05)

page = st.sidebar.radio("🧭 Navigate", ["Assessment", "Simulation & Comparison", "ROI & Recommendations"])

# -------------------------
# HELPER FUNCTIONS
# -------------------------
def get_score_from_choice(choice, options):
    for txt, val in options:
        if txt == choice:
            return val
    return 1

def radar_chart(categories, values, title=""):
    N = len(categories)
    angles = [n/float(N)*2*pi for n in range(N)]
    angles += angles[:1]
    vals = values + values[:1]
    fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))
    ax.set_theta_offset(pi/2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0,5)
    ax.plot(angles, vals, linewidth=2)
    ax.fill(angles, vals, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_title(title)
    return fig

# -------------------------
# PAGE 1: ASSESSMENT
# -------------------------
if page == "Assessment":
    st.header("📊 Industry 4.0 Readiness Assessment")

    c1, c2 = st.columns(2)
    with c1:
        tech_choice = st.selectbox("Technology", [o for o,_ in TECH_OPTIONS], index=2)
        proc_choice = st.selectbox("Process Integration", [o for o,_ in PROCESS_OPTIONS], index=2)
        people_choice = st.selectbox("People & Skills", [o for o,_ in PEOPLE_OPTIONS], index=2)
    with c2:
        data_choice = st.selectbox("Data & Analytics", [o for o,_ in DATA_OPTIONS], index=2)
        strat_choice = st.selectbox("Strategy & Governance", [o for o,_ in STRATEGY_OPTIONS], index=2)

    scores = {
        "Technology": get_score_from_choice(tech_choice, TECH_OPTIONS),
        "Process": get_score_from_choice(proc_choice, PROCESS_OPTIONS),
        "People": get_score_from_choice(people_choice, PEOPLE_OPTIONS),
        "Data": get_score_from_choice(data_choice, DATA_OPTIONS),
        "Strategy": get_score_from_choice(strat_choice, STRATEGY_OPTIONS)
    }

    if use_standard_weights:
        weights = STANDARD_WEIGHTS.copy()
    else:
        raw = {"Technology":w_tech, "Process":w_proc, "People":w_people, "Data":w_data, "Strategy":w_strat}
        s = sum(raw.values()) if sum(raw.values())>0 else 1
        weights = {k: raw[k]/s for k in raw}

    i4ri = sum(weights[d]*scores[d] for d in scores)

    if i4ri < 1.5:
        level = 'Level 1 — Manual / Basic'
    elif i4ri < 2.5:
        level = 'Level 2 — Digital Initiation'
    elif i4ri < 3.5:
        level = 'Level 3 — Connected Operations'
    elif i4ri < 4.25:
        level = 'Level 4 — Predictive / Smart'
    else:
        level = 'Level 5 — Smart / Autonomous'

    st.session_state['i4ri'] = i4ri
    st.session_state['level'] = level

    st.subheader("Results")
    c1, c2 = st.columns(2)
    c1.metric("I4.0 Readiness Index", f"{i4ri:.2f} / 5.00")
    c2.metric("Maturity Level", level)

    df = pd.DataFrame({
        "Score":[scores[k] for k in scores],
        "Weight":[weights[k] for k in scores]
    }, index=list(scores.keys()))
    st.subheader("Dimension Scores & Weights")
    st.table(df.style.format({"Score":"{:.0f}","Weight":"{:.2f}"}))

    st.subheader("Radar Chart")
    fig = radar_chart(list(scores.keys()), [scores[k] for k in scores], f"I4RI={i4ri:.2f}")
    st.pyplot(fig)

# -------------------------
# PAGE 2: SIMULATION & COMPARISON
# -------------------------
elif page == "Simulation & Comparison":
    st.header("🧩 Simulation-Based Performance Insights")
    st.image("assets/cnc_diagram.png", use_column_width=True)

    level = st.session_state.get('level', "Level 2 — Digital Initiation")
    if "Level 1" in level or "Level 2" in level:
        scenario = "baseline"
    elif "Level 3" in level:
        scenario = "connected"
    else:
        scenario = "predictive"

    st.success(f"Simulation results for: {level}")

    base_path = "simulation/precomputed_results"
    paths = {
        "baseline": os.path.join(base_path,"baseline.csv"),
        "connected": os.path.join(base_path,"connected.csv"),
        "predictive": os.path.join(base_path,"predictive.csv")
    }

    if os.path.exists(paths[scenario]):
        df_sel = pd.read_csv(paths[scenario])
        avg_th = df_sel['throughput_per_hr'].mean()
        avg_lt = df_sel['avg_lead_time_min'].mean()
        avg_down = df_sel['downtime_total_min'].mean()
        avg_q = df_sel['quality_rate'].mean()

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Throughput (units/hr)", f"{avg_th:.2f}")
        c2.metric("Lead Time (min)", f"{avg_lt:.1f}")
        c3.metric("Downtime (min)", f"{avg_down:.1f}")
        c4.metric("Quality Rate (%)", f"{avg_q*100:.1f}")

        st.subheader("Replication-wise variation")
        st.bar_chart(df_sel[['throughput_per_hr','avg_lead_time_min']])

        st.subheader("Scenario Comparison — Baseline vs Connected vs Predictive")
        comp_data = []
        for k,p in paths.items():
            if os.path.exists(p):
                dft = pd.read_csv(p)
                comp_data.append({
                    "Scenario":k.title(),
                    "Throughput":dft['throughput_per_hr'].mean(),
                    "Lead Time":dft['avg_lead_time_min'].mean(),
                    "Downtime":dft['downtime_total_min'].mean(),
                    "Quality":dft['quality_rate'].mean()
                })
        comp_df = pd.DataFrame(comp_data).set_index("Scenario")
        st.table(comp_df.round(3))
        st.bar_chart(comp_df[['Lead Time','Throughput']])

        st.subheader("Insights")
        if scenario == "baseline":
            st.write("Lower throughput and higher lead time. Focus on adding sensors and standardizing operations.")
        elif scenario == "connected":
            st.write("Improved throughput and reduced downtime. Focus on analytics and MES integration.")
        else:
            st.write("High performance with predictive control. Focus on optimization and scaling digital twins.")
    else:
        st.warning("Run `simulation/runner.py` first to generate data.")

# -------------------------
# PAGE 3: ROI & RECOMMENDATIONS
# -------------------------
elif page == "ROI & Recommendations":
    st.header("💰 ROI & Strategic Recommendations")

    p_base = "simulation/precomputed_results/baseline.csv"
    p_pred = "simulation/precomputed_results/predictive.csv"

    if os.path.exists(p_base) and os.path.exists(p_pred):
        dfb = pd.read_csv(p_base)
        dfp = pd.read_csv(p_pred)

        base_th = dfb['throughput_per_hr'].mean()
        pred_th = dfp['throughput_per_hr'].mean()
        base_lt = dfb['avg_lead_time_min'].mean()
        pred_lt = dfp['avg_lead_time_min'].mean()
        base_q = dfb['quality_rate'].mean()
        pred_q = dfp['quality_rate'].mean()

        st.write(f"Throughput: {base_th:.2f} → {pred_th:.2f}")
        st.write(f"Lead Time (min): {base_lt:.1f} → {pred_lt:.1f}")
        st.write(f"Quality Rate: {base_q:.3f} → {pred_q:.3f}")

        price_unit = st.number_input("Revenue per unit (₹)", value=10000.0)
        op_cost_hr = st.number_input("Operating cost per hour (₹)", value=1500.0)
        invest_cost = st.number_input("Estimated investment (₹)", value=200000.0)
        shift_hours = st.number_input("Shift duration (hours)", value=8.0)

        delta_th = pred_th - base_th
        added_rev = delta_th * price_unit * shift_hours
        units_base = base_th * shift_hours
        time_saved_hr = (base_lt - pred_lt) / 60.0 * units_base
        cost_savings = time_saved_hr * op_cost_hr
        defect_gain = (pred_q - base_q) * price_unit * units_base

        total_gain = added_rev + cost_savings + defect_gain
        roi = (total_gain - invest_cost) / invest_cost * 100

        st.subheader("Shift-level Financial Impact")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Added Revenue (₹)", f"{int(added_rev):,}")
        c2.metric("Savings (₹)", f"{int(cost_savings):,}")
        c3.metric("Defect Reduction Benefit (₹)", f"{int(defect_gain):,}")
        c4.metric("Estimated ROI (%)", f"{roi:.2f}")

        st.subheader("📘 Phase-wise Strategic Plan")
        with st.expander("Phase 1: Short Term (0–6 months)", expanded=True):
            st.write("- Install sensors on key CNC machines")
            st.write("- Begin collecting downtime and production data")
            st.write("- Train operators on digital basics")
        with st.expander("Phase 2: Medium Term (6–18 months)"):
            st.write("- Deploy MES-lite or IoT platform for data collection")
            st.write("- Enable real-time dashboards for line supervisors")
            st.write("- Use analytics to schedule maintenance")
        with st.expander("Phase 3: Long Term (18+ months)"):
            st.write("- Integrate digital twins for performance optimization")
            st.write("- Implement AI-based predictive quality control")
            st.write("- Establish continuous improvement governance")

    else:
        st.warning("Simulation results missing. Run `simulation/runner.py` to generate baseline and predictive data.")

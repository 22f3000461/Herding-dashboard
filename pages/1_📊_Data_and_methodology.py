import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="📊 Data and Methodology – Herding dashboard",page_icon="📊", layout="wide")

# ---------- simple styling ----------
st.markdown(
    """
    <style>
    .main > div {
        max-width: 1100px;
        margin-left: auto;
        margin-right: auto;
    }
    .markdown-text-container p,
    .markdown-text-container li {
        font-size: 1.06rem;
        line-height: 1.6;
    }
    h2, h3 { font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Data and Methodology")
st.caption("How the CSAD herding model is built for indian markets")

# ---------- load regression summary ----------
@st.cache_data
def load_regime_summary(path: str):
    df = pd.read_csv(path)

    if "gamma2_Rm_sq" not in df.columns and "gamma2" in df.columns:
        df.rename(columns={"gamma2": "gamma2_Rm_sq"}, inplace=True)

    df["herding_strength"] = np.where(df["gamma2_Rm_sq"] < 0,
                                      -df["gamma2_Rm_sq"],
                                      0.0)
    df["is_baseline"] = df["regime_label"].astype(str).str.contains("1996-1999")

    labels = []
    for _, row in df.iterrows():
        g2 = row["gamma2_Rm_sq"]
        if row["is_baseline"]:
            labels.append("🧊 baseline (no herding)")
        elif g2 <= -0.06:
            labels.append("🐃 strong herding")
        elif g2 < 0:
            labels.append("🐑 mild herding")
        else:
            labels.append("🧊 no herding")
    df["herding_label"] = labels
    df.loc[df["is_baseline"], "herding_strength"] = 0.0
    return df

summary_df = load_regime_summary("data/csad_regression_summary_all_regimes.csv")
summary_df = summary_df.sort_values("regime_label")

# ---------- section: data sources ----------
st.subheader("1️⃣ Data sources and sample construction")

st.markdown(
    """
- **universe**: daily equity prices for broad indian stock universe  
  (large-cap, mid-cap, small-cap; constituents adjusted over time).  
- **frequency**: daily close-to-close returns.  
- **period**: 1996–2024, split into economic regimes.  
- **construction**:
  - adjust for stock splits / bonuses where needed  
  - remove days with missing prices on more than a threshold share of stocks  
  - keep only stocks with sufficient trading history inside each regime.
"""
)

st.markdown("### regime definition used in the study")

with st.container():
    tmp = summary_df[["regime_label", "n_obs", "herding_label"]].copy()
    tmp = tmp.rename(
        columns={
            "regime_label": "regime",
            "n_obs": "Trading days",
            "herding_label": "Behaviour tag"
        }
    )
    st.dataframe(tmp, use_container_width=True, height=250)

st.markdown("---")

# ---------- section: variables ----------
st.subheader("2️⃣ variables used in the csad model")

st.markdown(
    """
for each day *t* and each stock *i* inside a regime:

- \( R_{i,t} \) – daily return on stock *i*  
- \( R_{m,t} \) – value-weighted market portfolio return (constructed from the universe)  
- \( \text{CSAD}_t \) – cross-sectional absolute deviation of individual returns from the market

the csad measure is defined as:
"""
)

st.latex(r"\text{CSAD}_t = \frac{1}{N_t} \sum_{i=1}^{N_t} \left| R_{i,t} - R_{m,t} \right|")

st.markdown(
    """
where \( N_t \) is the number of stocks with valid returns on day *t*.
"""
)

st.markdown("---")

# ---------- section: regression specification ----------
# --------- section: regression specification ---------
st.subheader("📘 econometric model ｜ non-linear csad regression")

st.markdown(
    """
for each regime we run the **chang, cheng & khorana (2000)** style regression:

"""
)

# ---------------- PROPER LATEX EQUATION ----------------
st.latex(
    r"""
    \text{CSAD}_t \;=\; 
    \alpha 
    \;+\; \gamma_1 \lvert R_{m,t} \rvert 
    \;+\; \gamma_2 R_{m,t}^{2} 
    \;+\; \varepsilon_t
    """
)

# ---------------- INTERPRETATION ----------------
st.markdown(
    """
### interpretation

- \( \gamma_1 \) captures the **normal, linear** rise in dispersion as markets move  
- \( \gamma_2 \) captures **non-linear convergence** (the key herding signal):

    - if \( \gamma_2 \ge 0 \) → dispersion rises normally → investors behave independently  
    - if \( \gamma_2 < 0 \) → dispersion fails to rise or even **falls** in big moves → **herding**  

### estimation details

- estimation method: OLS with **robust (heteroskedasticity-consistent)** standard errors  
- sample: one regression estimated per regime  
- inference: the **t-statistic** of \( \gamma_2 \) determines whether herding is statistically meaningful  
"""
)

st.markdown("---")

# ---------- section: quick visual – data coverage ----------
st.subheader("4️⃣ data coverage by regime")

fig = px.bar(
    summary_df,
    x="regime_label",
    y="n_obs",
    color="herding_label",
    labels={
        "regime_label": "regime",
        "n_obs": "trading days",
        "herding_label": "behaviour tag"
    },
    title="trading days per regime and qualitative herding tag",
    color_discrete_map={
        "🧊 baseline (no herding)": "#60a5fa",   # blue
        "🐑 mild herding": "#f97373",            # mild red
        "🐃 strong herding": "#b91c1c",          # strong red
        "🧊 no herding": "#6b7280",
    }
)

fig.update_layout(
    xaxis_title="regime",
    yaxis_title="number of daily observations",
    legend_title="behaviour tag 🐃 / 🐑 / 🧊",
    bargap=0.25,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---", unsafe_allow_html=True)

# --- UNIVERSAL BUTTON STYLE (rounded rectangle, big, bold) ---
st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #22c55e !important;
    color: white !important;

    padding: 22px 65px !important;
    border-radius: 22px !important;     /* Rounded rectangle */

    font-size: 26px !important;
    font-weight: 800 !important;

    border: none !important;
    box-shadow: 0px 6px 16px rgba(0,0,0,0.40) !important;

    min-width: 420px !important;
    height: 78px !important;

    display: inline-block !important;
}

div.stButton > button:hover {
    background-color: #16a34a !important;
    transform: scale(1.03);
    transition: 0.15s ease-in-out;
}

.centered-btn {
    display: flex;
    justify-content: center;
    margin-top: 35px;
    margin-bottom: 35px;
}
</style>
""", unsafe_allow_html=True)
st.markdown("<div class='centered-btn'>", unsafe_allow_html=True)
if st.button("📉 Next: Rolling CSAD", key="go_roll"):
    st.switch_page("pages/2_📉_Rolling_CSAD.py")
st.markdown("</div>", unsafe_allow_html=True)




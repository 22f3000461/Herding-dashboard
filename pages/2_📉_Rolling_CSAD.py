import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title=" Rolling CSAD – Herding dashboard",
    page_icon="📉",
    layout="wide"
)

st.markdown(
    """
    <style>
    .main > div { max-width: 1100px; margin-left:auto; margin-right:auto; }
    .markdown-text-container p,
    .markdown-text-container li { font-size:1.06rem; line-height:1.6; }
    h2, h3 { font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title(" Rolling CSAD and Market Stress")
st.caption("watching dispersion dance around inside each market regime")

# yeah I hardcoded the files, sue me
REGIME_FILES = {
    "1996–1999  Baseline": "data/csad_1996_1999.csv",
    "1999–2007  Pre-GFC boom": "data/csad_1999_2007.csv",
    "2007–2009  GFC crisis": "data/csad_2007_2009.csv",
    "2015–2024  Modern era": "data/csad_2015_2024.csv",
    "2020–2022  Covid + ipo mania": "data/csad_2020_2022.csv",
}

@st.cache_data
def load_csad(path: str):
    df = pd.read_csv(path)
    # dayfirst because whoever formatted these dates had their own ideas
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    return df

st.subheader("Pick your regime and window size")

regime_name = st.selectbox("regime", list(REGIME_FILES.keys()), index=3)
window = st.slider(
    "rolling window (days)", 
    min_value=20, 
    max_value=250, 
    value=60, 
    step=10
)

df = load_csad(REGIME_FILES[regime_name])

# bail if the data's busted
if "CSAD" not in df.columns:
    st.error("yo, CSAD column is missing from this file. check your data.")
    st.stop()

# calculate rolling averages
df = df.set_index("date")
df["csad_roll"] = df["CSAD"].rolling(window).mean()

# only calc market return rolling avg if it exists
if "Rm" in df.columns:
    df["Rm_abs_roll"] = df["Rm"].abs().rolling(window).mean()
else:
    df["Rm_abs_roll"] = np.nan

df = df.reset_index()

st.markdown("### Rolling average CSAD over time")

fig1 = px.line(
    df,
    x="date",
    y="csad_roll",
    title=f"{window}-day rolling CSAD – {regime_name}"
)
fig1.update_layout(
    xaxis_title="date",
    yaxis_title=f"CSAD (rolling {window}d avg)",
)
st.plotly_chart(fig1, use_container_width=True)

# only show market return plot if we actually have the data
if df["Rm_abs_roll"].notna().any():
    st.markdown("### Rolling average absolute market return")
    fig2 = px.line(
        df,
        x="date",
        y="Rm_abs_roll",
        title=f"{window}-day rolling |Rₘ| – {regime_name}"
    )
    fig2.update_layout(
        xaxis_title="date",
        yaxis_title=f"|Rₘ| (rolling {window}d avg)",
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown(
    """
what you're looking at:

- **big spikes in rolling CSAD** → stocks went wild for days on end  
- **CSAD tanks while |Rₘ| stays high** → everyone's moving together = **herding**  

this gives you the story behind that static γ₂ coefficient from your regression.
"""
)

st.markdown("---", unsafe_allow_html=True)

# big chunky button styling because default streamlit buttons are wimpy
st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #22c55e !important;
    color: white !important;
    padding: 22px 65px !important;
    border-radius: 22px !important;
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
if st.button(" Next: Regime Explorer", key="go_regime"):
    st.switch_page("pages/3_🔍_Regime_explorer.py")
st.markdown("</div>", unsafe_allow_html=True)
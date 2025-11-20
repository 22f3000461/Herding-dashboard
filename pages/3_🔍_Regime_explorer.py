import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="🔍 Regime explorer – Herding dashboard",
    page_icon="🔍",
    layout="wide"
)
st.markdown("""
<style>
html, body, [class*="css"], .markdown-text-container {
    font-size: 20px !important;
    line-height: 1.75 !important;
}
</style>
""", unsafe_allow_html=True)



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

st.title("🔍 Regime Explorer")
st.caption("Zoom into one regime: prices, market return, and CSAD shape")

REGIME_CSAD = {
    "🧊1996–1999  Baseline": "data/csad_1996_1999.csv",
    "📈1999–2007  Pre-GFC boom": "data/csad_1999_2007.csv",
    "💥2007–2009  GFC crisis": "data/csad_2007_2009.csv",
    "📱2015–2024  Modern era": "data/csad_2015_2024.csv",
    "😷2020–2022  Covid + IPO mania": "data/csad_2020_2022.csv",
}

@st.cache_data
def load_csad(path: str):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    return df

@st.cache_data
def load_summary(path: str):
    df = pd.read_csv(path)
    if "gamma2_Rm_sq" not in df.columns and "gamma2" in df.columns:
        df.rename(columns={"gamma2": "gamma2_Rm_sq"}, inplace=True)
    return df

summary_df = load_summary("data/csad_regression_summary_all_regimes.csv")

st.subheader("1️⃣ Select Regime")

regime_name = st.selectbox("regime", list(REGIME_CSAD.keys()), index=3)
csad_df = load_csad(REGIME_CSAD[regime_name])

# reconstruct simple index from Rm if available
if "Rm" in csad_df.columns:
    csad_df["index_level"] = 100 * (1 + csad_df["Rm"]).cumprod()
else:
    csad_df["index_level"] = np.nan

# quick stats from regression summary
if summary_df is not None:
    # try to match by substring
    match = summary_df[summary_df["regime_label"].astype(str).str.contains(regime_name.split()[0])]
    if not match.empty:
        row = match.iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("γ₂ (Rm²)", f"{row['gamma2_Rm_sq']:.4f}")
        c2.metric("mean CSAD", f"{row['mean_CSAD']:.4f}")
        c3.metric("days in regime", int(row["n_obs"]))

st.markdown("---")

st.subheader("2️⃣ Price index and CSAD over time")

c1, c2 = st.columns(2)

with c1:
    fig_price = px.line(
        csad_df,
        x="date",
        y="index_level",
        title=f"reconstructed market index – {regime_name}"
    )
    fig_price.update_layout(xaxis_title="date", yaxis_title="index (base = 100)")
    st.plotly_chart(fig_price, use_container_width=True)

with c2:
    fig_csad = px.line(
        csad_df,
        x="date",
        y="CSAD",
        title=f"csad over time – {regime_name}"
    )
    fig_csad.update_layout(xaxis_title="date", yaxis_title="CSAD")
    st.plotly_chart(fig_csad, use_container_width=True)

st.markdown("---")

st.subheader("3️⃣ CSAD vs |Rₘ| – Curvature check")

if "abs_Rm" in csad_df.columns:
    fig_scatter = px.scatter(
        csad_df,
        x="abs_Rm",
        y="CSAD",
        opacity=0.5,
        title=f"csad vs |Rₘ| – {regime_name}"
    )

    try:
        x = csad_df["abs_Rm"].values
        y = csad_df["CSAD"].values
        a, b, c = np.polyfit(x, y, 2)
        grid = np.linspace(x.min(), x.max(), 200)
        fit = a * grid**2 + b * grid + c
        fig_scatter.add_scatter(
            x=grid,
            y=fit,
            mode="lines",
            name="quadratic fit"
        )
    except Exception:
        pass

    fig_scatter.update_layout(
        xaxis_title="|Rₘ|",
        yaxis_title="CSAD",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown(
        """
reading this plot:

- if the fitted curve is **roughly linear or upward** → dispersion increases with |Rₘ| → normal behaviour  
- if it **bends down** at high |Rₘ| → dispersion collapses in big moves → sign of **herding**
"""
    )
else:
    st.warning("abs_Rm column missing in this csad file; cannot draw curvature plot.")
st.markdown("---", unsafe_allow_html=True)

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
if st.button("🦠 Next: Covid Window", key="go_covid"):
    st.switch_page("pages/4_🦠_Covid_window.py")
st.markdown("</div>", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="🦠 Covid window – Herding dashboard",
    page_icon="🦠",
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

st.title("🦠 Covid window: Crash, Rebound, and IPO Mania")
st.caption("focusing on 2020–2022 Regime")

@st.cache_data
def load_csad(path: str):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    return df

covid_df = load_csad("data/csad_2020_2022.csv")

if "Rm" in covid_df.columns:
    covid_df["index_level"] = 100 * (1 + covid_df["Rm"]).cumprod()
else:
    covid_df["index_level"] = np.nan

st.subheader("1️⃣ Price and CSAD during covid window")

c1, c2 = st.columns(2)

with c1:
    fig_price = px.line(
        covid_df,
        x="date",
        y="index_level",
        title="reconstructed market index – covid window"
    )
    fig_price.update_layout(xaxis_title="date", yaxis_title="index (base = 100)")
    st.plotly_chart(fig_price, use_container_width=True)

with c2:
    fig_csad = px.line(
        covid_df,
        x="date",
        y="CSAD",
        title="csad over time – covid window"
    )
    fig_csad.update_layout(xaxis_title="date", yaxis_title="CSAD")
    st.plotly_chart(fig_csad, use_container_width=True)

st.markdown("---")

st.subheader("2️⃣ CSAD vs |Rₘ| in covid Regime")

if "abs_Rm" in covid_df.columns:
    fig_scatter = px.scatter(
        covid_df,
        x="abs_Rm",
        y="CSAD",
        opacity=0.5,
        title="csad vs |Rₘ| – covid window (2020–2022)"
    )

    try:
        x = covid_df["abs_Rm"].values
        y = covid_df["CSAD"].values
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
interpretation:

- left side of the window: **panic crash** – high |Rₘ| with csad reacting sharply  
- middle: **stimulus + recovery** – herding may flip from panic selling to fomo buying  
- later: **ipo mania** – many days with small cross-sectional dispersion despite strong index moves  
this regime is where retail and social-media-driven behaviour shows up most clearly.
"""
)
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
if st.button("🧩 Next: Conclusion", key="go_conclusion"):
    st.switch_page("pages/5_🧩_Conclusion_limitation_reference.py")
st.markdown("</div>", unsafe_allow_html=True)


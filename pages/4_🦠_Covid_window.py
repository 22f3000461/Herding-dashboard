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

st.title("🦠 Covid Window: Crash, Rebound, and IPO Mania")
st.caption("the wildest market period in recent memory – panic, stimulus checks, and meme stocks")

@st.cache_data
def load_csad(path: str):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    return df

covid_df = load_csad("data/csad_2020_2022.csv")

# build fake index from returns
if "Rm" in covid_df.columns:
    covid_df["index_level"] = 100 * (1 + covid_df["Rm"]).cumprod()
else:
    covid_df["index_level"] = np.nan

st.subheader("What happened to prices and dispersion")

c1, c2 = st.columns(2)

with c1:
    fig_price = px.line(
        covid_df,
        x="date",
        y="index_level",
        title="market index during covid era"
    )
    fig_price.update_layout(xaxis_title="date", yaxis_title="index level (starts at 100)")
    st.plotly_chart(fig_price, use_container_width=True)

with c2:
    fig_csad = px.line(
        covid_df,
        x="date",
        y="CSAD",
        title="CSAD through the chaos"
    )
    fig_csad.update_layout(xaxis_title="date", yaxis_title="CSAD")
    st.plotly_chart(fig_csad, use_container_width=True)

st.markdown("---")

st.subheader("Did everyone panic together or separately?")

if "abs_Rm" in covid_df.columns:
    fig_scatter = px.scatter(
        covid_df,
        x="abs_Rm",
        y="CSAD",
        opacity=0.5,
        title="CSAD vs |Rₘ| during covid (2020–2022)"
    )

    # fit a curve to see if it bends weird
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
        # sometimes the math just doesn't want to cooperate
        pass

    fig_scatter.update_layout(
        xaxis_title="|Rₘ|",
        yaxis_title="CSAD",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown(
    """
what's actually going on here:

- **early 2020 (left edge):** absolute panic selling – market dropped 30%+ in weeks, everyone rushing for the exits  
- **mid-2020:** fed printer goes brrr, stimulus checks hit, retail traders flood in  
- **2021–2022:** IPO frenzy, SPACs everywhere, meme stocks moon – low dispersion because everyone's chasing the same hype  

this is where you see social media and retail behavior mess with traditional herding patterns. wsb wasn't around in 2008.
"""
)

st.markdown("---", unsafe_allow_html=True)

# big friendly button
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
if st.button("🧩 Next: Conclusion", key="go_conclusion"):
    st.switch_page("pages/5_🧩_Conclusion_limitation_reference.py")
st.markdown("</div>", unsafe_allow_html=True)
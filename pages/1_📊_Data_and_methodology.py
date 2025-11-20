import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="📊 Data and Methodology – Herding dashboard",
    page_icon="📊", 
    layout="wide"
)

# CSS tweaks - took forever to get the spacing right
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

st.title("📊 Data & Methodology")
st.caption("Breaking down how we analyzed 28 years of Indian market data")

# Load the regime summary data
@st.cache_data
def load_regime_summary(path: str):
    df = pd.read_csv(path)
    
    # sometimes the column name comes out as 'gamma2' instead of 'gamma2_Rm_sq'
    if "gamma2_Rm_sq" not in df.columns and "gamma2" in df.columns:
        df.rename(columns={"gamma2": "gamma2_Rm_sq"}, inplace=True)

    # calculate herding strength - only negative gamma2 matters
    df["herding_strength"] = np.where(df["gamma2_Rm_sq"] < 0,
                                      -df["gamma2_Rm_sq"],
                                      0.0)
    
    df["is_baseline"] = df["regime_label"].astype(str).str.contains("1996-1999")

    # assign readable tags
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


st.subheader(" Data sources & sample construction")

st.markdown(
    """
We pulled together daily stock prices across the Indian equity universe - everything from blue-chip large-caps 
down to smaller mid and small-cap names. The exact list of stocks changed over time (companies get listed, 
delisted, merged... you know how it goes).

**What we worked with:**
- Daily closing prices from 1996 through 2024
- Returns calculated as simple day-over-day percentage changes
- Split the data into distinct market regimes based on economic conditions

**Data cleaning (the tedious part):**
- Handled corporate actions - stock splits, bonus issues, etc.
- Filtered out days where too many stocks had missing data (usually around holidays or system glitches)
- Set minimum thresholds for each stock's trading history within a regime - if a stock barely traded, we excluded it

The goal was to have a clean, consistent dataset for each regime without introducing survivorship bias.
"""
)

st.markdown("### Market regimes we analyzed")

with st.container():
    tmp = summary_df[["regime_label", "n_obs", "herding_label"]].copy()
    tmp = tmp.rename(
        columns={
            "regime_label": "Period",
            "n_obs": "Days analyzed",
            "herding_label": "Finding"
        }
    )
    st.dataframe(tmp, use_container_width=True, height=250)

st.markdown("---")


st.subheader(" Key variables")

st.markdown(
    """
For every single trading day in our sample, we calculated three main things:

**Individual stock return** - \( R_{i,t} \)  
Pretty straightforward: (Today's close - Yesterday's close) / Yesterday's close for each stock

**Market return** - \( R_{m,t} \)  
The overall portfolio return, calculated as a value-weighted average across all stocks in the universe that day

**CSAD (Cross-Sectional Absolute Deviation)** - \( \text{CSAD}_t \)  
This is the key metric. It measures dispersion - basically "how spread out were individual stock returns compared to the market?"
"""
)

st.latex(r"\text{CSAD}_t = \frac{1}{N_t} \sum_{i=1}^{N_t} \left| R_{i,t} - R_{m,t} \right|")

st.markdown(
    """
\( N_t \) = number of stocks with valid data on day *t*

Think of it this way: if the market goes up 1% and every single stock also goes up exactly 1%, then CSAD = 0. 
Perfect synchronization. But if stocks are all over the place - some up 5%, some down 3%, some flat - then CSAD is high.

When herding happens, CSAD doesn't grow like it should during big market moves. It stays compressed.
"""
)

st.markdown("---")


st.subheader("📘 The regression model (non-linear CSAD)")

st.markdown(
    """
We're using the **Chang, Cheng & Khorana (2000)** framework here. It's become the standard approach for 
detecting herding in equity markets. Here's the equation we estimate separately for each regime:
"""
)

st.latex(
    r"""
    \text{CSAD}_t \;=\; 
    \alpha 
    \;+\; \gamma_1 \lvert R_{m,t} \rvert 
    \;+\; \gamma_2 R_{m,t}^{2} 
    \;+\; \varepsilon_t
    """
)

st.markdown(
    """
### Breaking it down

**α (alpha)** - Just the intercept, tells us the baseline CSAD level

**γ₁ (gamma 1)** - Linear term  
Captures normal market behavior. Usually positive because when markets move a lot (up or down), 
individual stocks naturally show more dispersion. Different stocks react differently to news.

**γ₂ (gamma 2)** - Quadratic term ← *This is what we care about*  
Tests for non-linearity. Under normal conditions, this should be positive or at worst zero.  
But if γ₂ is significantly **negative**, that's your herding signal.

Why? Because negative γ₂ means dispersion actually *decreases* or fails to increase properly when market 
movements get large. Everyone's piling in the same direction instead of thinking independently.

### Technical details

- Estimation: Standard OLS regression
- Standard errors: Robust (Newey-West style) to handle heteroskedasticity and potential autocorrelation
- One regression per regime (so we can see how herding changes across different market conditions)
- Statistical significance tested via t-stats on γ₂

We're looking for γ₂ < 0 with a significant t-stat. That combination = herding confirmed.
"""
)

st.markdown("---")


st.subheader("Sample coverage by period")

st.write(
    "Each regime has a different sample size depending on how long that period lasted. "
    "More trading days = more robust estimates."
)

fig = px.bar(
    summary_df,
    x="regime_label",
    y="n_obs",
    color="herding_label",
    labels={
        "regime_label": "Regime",
        "n_obs": "Trading days",
        "herding_label": "Classification"
    },
    title="Sample size and herding classification by regime",
    color_discrete_map={
        "🧊 baseline (no herding)": "#60a5fa",
        "🐑 mild herding": "#f97373",
        "🐃 strong herding": "#b91c1c",
        "🧊 no herding": "#6b7280",
    }
)

fig.update_layout(
    xaxis_title="Market regime",
    yaxis_title="Number of trading days analyzed",
    legend_title="Behavior type",
    bargap=0.25,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Button styling - keeping the green theme consistent
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
if st.button("📉 Next: Rolling CSAD Analysis", key="go_roll"):
    st.switch_page("pages/2_📉_Rolling_CSAD.py")
st.markdown("</div>", unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# page setup
st.set_page_config(
    page_title="Home-Herding in Indian Equity Markets",
    page_icon="🏠",
    layout="wide"
)

# custom styling - spent way too much time on this
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
    
    h2, h3 {
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title(" Herding Behaviour in Indian equity markets")
st.caption(" Non-linear CSAD model across market regimes (1996–2024)")

# load and prep the regime data
@st.cache_data
def load_regime_summary(path: str):
    df = pd.read_csv(path)

    # fixing column name if needed
    if "gamma2_Rm_sq" not in df.columns and "gamma2" in df.columns:
        df.rename(columns={"gamma2": "gamma2_Rm_sq"}, inplace=True)

    # herding strength calculation - only counts when gamma2 is negative
    df["herding_strength"] = np.where(df["gamma2_Rm_sq"] < 0,
                                      -df["gamma2_Rm_sq"],
                                      0.0)

    # baseline is our reference point
    df["is_baseline"] = df["regime_label"].astype(str).str.contains("1996-1999")

    # adding readable labels for each regime
    labels = []
    for _, row in df.iterrows():
        g2 = row["gamma2_Rm_sq"]
        if row["is_baseline"]:
            labels.append(" Baseline (no herding)")
        elif g2 <= -0.06:
            labels.append(" Strong herding")
        elif g2 < 0:
            labels.append(" Mild herding")
        else:
            labels.append(" no herding")
    df["herding_label"] = labels

    df.loc[df["is_baseline"], "herding_strength"] = 0.0

    return df


summary_path = "data/csad_regression_summary_all_regimes.csv"
summary_df = load_regime_summary(summary_path)
summary_df = summary_df.sort_values("regime_label")


# quick stats section
st.subheader("Quick Project Snapshot")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Regimes Analysed", value=len(summary_df))

with col2:
    total_obs = int(summary_df["n_obs"].sum())
    st.metric("Trading days", value=f"{total_obs:,}")

non_base = summary_df[~summary_df["is_baseline"]].copy()

with col3:
    strongest = non_base.loc[non_base["herding_strength"].idxmax()]
    st.metric(
        "peak herding (vs baseline)",
        value=f"{strongest['regime_label']}",
        delta=f"HSI = {strongest['herding_strength']:.3f}"
    )

with col4:
    weakest = non_base.loc[non_base["herding_strength"].idxmin()]
    st.metric(
        " Independent (non-baseline)",
        value=f"{weakest['regime_label']}",
        delta=f"HSI = {weakest['herding_strength']:.3f}"
    )

st.markdown("---")


# explaining herding behavior
st.subheader(" What is Herding?")

left_col, right_col = st.columns([2, 1])

with left_col:
    st.markdown(
        """
Herding is basically when investors stop thinking independently and start copying each other.

Think of it like this:

-  **Copy-paste trading** – "If the big players are buying X, I should too"
-  **FOMO kicks in** – "Everyone's jumping into small-caps, can't miss out"
-  **Ignoring your own analysis** – Deep down you know it's time to sell, but you buy anyway because "the market knows best"

Normally after news breaks:
- Some traders feel bullish
- Others think it's bearish
- Returns spread out across stocks because people actually disagree

But when herding happens:
- Everyone rushes to the same side
- Stock returns cluster together 
- The whole market moves like one giant crowd instead of thousands of independent decisions
"""
    )

with right_col:
    st.info(
        "🔍 Think about it:\n\n"
        "Imagine 100 students picking college electives.\n\n"
        "Independent choices → diverse mix of subjects picked.\n\n"
        "Everyone copying the toppers → same 2-3 subjects dominate.\n\n"
        "That copying behavior? That's herding."
    )

st.markdown("---")


# project goals
st.subheader(" What are we actually trying to show?")

st.markdown(
    """
This dashboard answers three big questions:

1. **Does herding even exist** in Indian markets between 1996 and 2024?
2. **Is it constant**, or does it spike during crises and mania phases?
3. **Does herding only show up when markets move aggressively?**  
   (Meaning calm days = rational, volatile days = stampede)

How we approached it:

- Split 28 years into distinct **market regimes**:
  -  **1996–1999** – Our baseline (thinner market, less retail participation)
  -  **1999–2007** – Boom years leading up to the global crisis
  -  **2007–2009** – The financial crisis period
  -  **2015–2024** – Modern era with digital trading & retail boom
  -  **2020–2022** – COVID crash followed by IPO frenzy
  
- Calculated **daily CSAD** for each regime
- Ran the **non-linear CSAD regression** and compared γ₂ values across periods
"""
)

st.markdown("---")


# CSAD explanation
st.subheader(" What exactly is CSAD?")

st.markdown(
    """
To detect herding, we need something that measures:

> "How far are individual stock returns from the overall market return on any given day?"

That's where **CSAD (Cross-Sectional Absolute Deviation)** comes in:
"""
)

st.latex(r"\text{CSAD}_t = \frac{1}{N}\sum_{i=1}^{N} \left| R_{i,t} - R_{m,t} \right|")
st.caption("N = number of stocks, R_{i,t} = return of stock i, R_{m,t} = market return on day t")

st.markdown(
    """
What it tells us:

- **High CSAD** → Investors are disagreeing, stocks moving independently from the index
- **Low CSAD** → Everyone's moving together, returns clustering around market return

**Quick example with actual numbers:**

Let's say the market return is +0.5% (0.005) and we have 4 stocks:
"""
)

# example calculation
toy_df = pd.DataFrame(
    {
        "stock": ["A", "B", "C", "D"],
        "return": [-0.010, 0.000, 0.010, 0.020],
    }
)
Rm = 0.005
toy_df["|Ri − Rm|"] = (toy_df["return"] - Rm).abs()
csad_example = toy_df["|Ri − Rm|"].mean()

with st.container():
    st.markdown(
        """
        <div style="
            background-color: rgba(148, 163, 184, 0.12);
            padding: 8px 10px;
            border-radius: 10px;
            border: 1px solid rgba(148, 163, 184, 0.5);
        ">
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(
        toy_df.style.format({"return": "{:.3f}", "|Ri − Rm|": "{:.3f}"}),
        use_container_width=True,
        height=200,
    )
    st.markdown("</div>", unsafe_allow_html=True)

numeric_eq = r"\text{CSAD} = \frac{1}{4}\sum |R_i - R_m| = %.3f" % csad_example
st.markdown(
    """
Here's the math:

- Market return = 0.005
- Average dispersion:
"""
)
st.latex(numeric_eq)
st.markdown(
    """
If all stocks moved almost identically to the market,  
these deviations would be tiny and CSAD would approach zero → **extreme crowding/herding**.
"""
)

st.markdown("---")


# why CSAD specifically
st.subheader(" Why use CSAD instead of other measures?")

c1, c2 = st.columns(2)

with c1:
    st.markdown(
        """
**Other options we considered (and why they didn't work):**

-  **Index volatility**  
  Only shows how much the index bounces around. Doesn't tell us anything about whether individual stocks are moving together or independently. High volatility can happen with OR without herding.

-  **Average correlations**  
  Requires massive correlation matrices and still doesn't directly capture the non-linear convergence we're looking for.

-  **CSSD (cross-sectional standard deviation)**  
  Too sensitive to outliers. One or two crazy stocks can throw off the entire measure.

The problem? These metrics mix up:
- "The market is just volatile right now"  
- versus "The market is literally herding"
"""
    )

with c2:
    st.markdown(
        """
**Why CSAD works better for us:**

- Handles **large cross-sections** well (we're looking at Nifty + broader universe)
- Uses **absolute deviations**, so outliers don't wreck everything
- Fits perfectly into the **Chang, Cheng & Khorana (2000)** framework:
"""
    )
    st.latex(r"\text{CSAD}_t = \alpha + \gamma_1 |R_{m,t}| + \gamma_2 R_{m,t}^2 + \varepsilon_t")
    st.latex(r"\gamma_2 < 0 \;\Rightarrow\; \text{herding detected}")

st.markdown(
    """
Bottom line: CSAD gives us:
- A **daily herding indicator** (one clean number per trading day)
- A clear statistical test: if γ₂ comes out significantly negative, dispersion isn't growing with large market moves → **herding confirmed**
"""
)

st.markdown("---")


# visualization of herding by regime
st.subheader(" Which periods showed stronger herding?")

st.write(
    "These bars show **herding intensity relative to our 1996-1999 baseline**. "
    "We only count negative γ₂ values as evidence of herding."
)

fig = px.bar(
    summary_df,
    x="regime_label",
    y="herding_strength",
    color="herding_label",
    text="herding_label",
    labels={
        "regime_label": "regime",
        "herding_strength": "Herding Strength (−γ₂)",
        "herding_label": "Herding Category"
    },
    color_discrete_map={
        "🧊 Baseline (no herding)": "#60a5fa",
        "🐑 Mild herding": "#f97373",
        "🐃 Strong herding": "#b91c1c",
        "🧊 no herding": "#6b7280",
    }
)

fig.update_traces(
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>HSI = %{y:.4f}<br>%{text}<extra></extra>"
)
fig.update_layout(
    title="Herding intensity across different market regimes",
    xaxis_title="Market regime",
    yaxis_title="Herding strength vs baseline",
    legend_title="Behavior type",
    bargap=0.25,
)

st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """
Legend breakdown:
-  **Baseline** → Reference period (1996-1999), no herding detected
-  **Strong herding** → Crisis/mania periods like GFC and COVID
-  **Mild herding** → Some convergence but stocks still maintain individuality
-  **No herding** → Market behaving rationally with independent decision-making
"""
)

st.markdown("---")


# detailed table
st.subheader(" Detailed regression results by regime")

table_cols = ["regime_label", "n_obs", "mean_CSAD", "gamma2_Rm_sq", "herding_strength", "herding_label"]
table_df = summary_df[table_cols].copy()
table_df["mean_CSAD"] = table_df["mean_CSAD"].round(4)
table_df["gamma2_Rm_sq"] = table_df["gamma2_Rm_sq"].round(4)
table_df["herding_strength"] = table_df["herding_strength"].round(4)

table_df = table_df.rename(
    columns={
        "regime_label": "regime",
        "n_obs": "trading days",
        "mean_CSAD": "Mean CSAD",
        "gamma2_Rm_sq": "γ₂ coefficient",
        "herding_strength": "herding strength",
        "herding_label": "behavior"
    }
)

def style_row(row):
    tag = row["behavior"]
    if "baseline" in tag.lower():
        color = "rgba(148, 163, 184, 0.18)"
    elif tag.startswith("🐃"):
        color = "rgba(220, 38, 38, 0.18)"
    elif tag.startswith("🐑"):
        color = "rgba(234, 179, 8, 0.18)"
    else:
        color = "rgba(37, 99, 235, 0.18)"
    return [f"background-color: {color}"] * len(row)

styled = table_df.style.apply(style_row, axis=1)

with st.expander(" Full regime summary (click to expand)", expanded=False):
    st.markdown(
        """
        <div style="
            background-color: rgba(15, 23, 42, 0.08);
            padding: 10px 12px;
            border-radius: 12px;
            border: 1px solid rgba(148, 163, 184, 0.6);
        ">
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(styled, use_container_width=True, height=260)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")


# navigation button styling
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
    display: inline-block;
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
if st.button("Next: Data & Methodology", key="go_data"):
    st.switch_page("pages/1_📊_Data_and_methodology.py")
st.markdown("</div>", unsafe_allow_html=True)
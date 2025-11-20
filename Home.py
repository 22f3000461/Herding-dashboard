import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ----------------- BASIC PAGE CONFIG -----------------
st.set_page_config(
    page_title="🏠Home-Herding in Indian Equity Markets",
    page_icon="🏠",
    layout="wide"
)

# ------------- GLOBAL STYLING (TEXT SIZE + CENTER) -------------
st.markdown(
    """
    <style>
    /* Keep content width reasonable */
    .main > div {
        max-width: 1100px;
        margin-left: auto;
        margin-right: auto;
    }
    /* Make paragraphs and list items a bit larger */
    .markdown-text-container p,
    .markdown-text-container li {
        font-size: 1.06rem;
        line-height: 1.6;
    }
    /* Slightly bolder section headings */
    h2, h3 {
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📈 Herding Behaviour in Indian equity markets")
st.caption("🧮 Non-linear CSAD model across market regimes (1996–2024)")

# =====================================================
# 1. LOAD REGIME SUMMARY
# =====================================================

@st.cache_data
def load_regime_summary(path: str):
    df = pd.read_csv(path)

    # expected: regime_label, gamma2_Rm_sq, n_obs, mean_CSAD
    if "gamma2_Rm_sq" not in df.columns and "gamma2" in df.columns:
        df.rename(columns={"gamma2": "gamma2_Rm_sq"}, inplace=True)

    # herding strength index: only negative gamma2 counts as herding
    df["herding_strength"] = np.where(df["gamma2_Rm_sq"] < 0,
                                      -df["gamma2_Rm_sq"],
                                      0.0)

    # mark baseline regime explicitly (assumes label contains "1996-1999")
    df["is_baseline"] = df["regime_label"].astype(str).str.contains("1996-1999")

    # qualitative tag for dashboard
    labels = []
    for _, row in df.iterrows():
        g2 = row["gamma2_Rm_sq"]
        if row["is_baseline"]:
            labels.append("🧊 Baseline (no herding)")
        elif g2 <= -0.06:
            labels.append("🐃 Strong herding")
        elif g2 < 0:
            labels.append("🐑 Mild herding")
        else:
            labels.append("🧊 no herding")
    df["herding_label"] = labels

    # baseline strength = 0 by design
    df.loc[df["is_baseline"], "herding_strength"] = 0.0

    return df


summary_path = "data/csad_regression_summary_all_regimes.csv"
summary_df = load_regime_summary(summary_path)
summary_df = summary_df.sort_values("regime_label")

# =====================================================
# 2. HIGH LEVEL STATS
# =====================================================

st.subheader("🔍 Quick Project Snapshot")

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

# =====================================================
# 3. Q&A – WHAT IS HERDING?
# =====================================================

st.subheader("1️⃣ 🐑 What is Herding?")

left_col, right_col = st.columns([2, 1])

with left_col:
    st.markdown(
        """
Herding is basically **stock market group-project behaviour**.

Instead of thinking for themselves, investors start doing:

- 🐑 *copy–paste trading* – “big FII is buying X? I’ll also buy X.”
- 😨 *FOMO* – “everyone is in small-caps, I should also jump in.”
- 🙈 Ignoring own information – your analysis says **sell**, but you buy because
  “market sab jaanta hai”.

In a normal market, after news:

- some traders are optimistic.  
- some are pessimistic.  

so returns are **spread out** – people disagree.

In **herding**:

- everyone piles on the **same side**
- dispersion across stocks **shrinks**
- the market behaves like **one crowd**, not many independent minds.
"""
    )

with right_col:
    st.info(
        "🔍 intuition:\n\n"
        "- imagine 100 students choosing electives.\n"
        "- if everyone chooses independently → mix of subjects.\n"
        "- if everyone copies toppers → same 2–3 subjects dominate.\n"
        "that copying behaviour is **herding**."
    )

st.markdown("---")

# =====================================================
# 4. Q&A – WHAT ARE WE TRYING TO SHOW?
# =====================================================

st.subheader("2️⃣ 🎯 What do we want to show through this project?")

st.markdown(
    """
This dashboard is trying to answer:

1. **Does herding actually exist** in Indian equity markets from 1996–2024?  
2. **Is herding the same in all regimes**, or does it spike only in crisis / mania?  
3. **Does herding switch on only when market moves are large?**  
   (non-linear behaviour – calm days look rational, stress days look like a stampede.)

we:

- split the sample into **regimes**  
  - 🧊 **1996–1999** – baseline reference, thin market, low retail  
  - 📈 **1999–2007** – boom + pre-GFC build-up  
  - 💥 **2007–2009** – global financial crisis  
  - 📱 **2015–2024** – modern era, digital & retail wave  
  - 😷 **2020–2022** – covid + IPO mania  
- compute **daily CSAD** for each regime  
- estimate the **non-linear CSAD regression** and compare γ₂ across regimes
"""
)

st.markdown("---")

# =====================================================
# 5. Q&A – WHAT IS CSAD? TOY EXAMPLE + LATEX
# =====================================================

st.subheader("3️⃣ 🧮 What is CSAD and what does it measure?")

st.markdown(
    """
To detect herding we need a number that answers:

> “on this day, how far were individual stock returns from the market return?”

that number is **CSAD – cross-sectional absolute deviation**:
"""
)

st.latex(r"\text{CSAD}_t = \frac{1}{N}\sum_{i=1}^{N} \left| R_{i,t} - R_{m,t} \right|")
st.caption("N = number of stocks, R_{i,t} = return of stock i, R_{m,t} = market return on day t.")

st.markdown(
    """
interpretation:

- if investors **disagree a lot**, individual returns are far from the market → CSAD is **high**  
- if everyone behaves similarly, individual returns hug the market → CSAD **collapses**

**tiny numeric example**

suppose on one day the market index return is +0.5% (0.005) and four stocks move like this:
"""
)

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
here:

- Market return \( R_m = 0.005 \)  
- average dispersion:
"""
)
st.latex(numeric_eq)
st.markdown(
    """
If everyone moved almost exactly like the market,  
\\( |R_i - R_m| \\) would be tiny and CSAD would be close to 0 → **very strong crowding**.
"""
)

st.markdown("---")

# =====================================================
# 6. Q&A – WHY CSAD AND NOT OTHER MEASURES?
# =====================================================

st.subheader("4️⃣ 📐 Why CSAD and not some other measure?")

c1, c2 = st.columns(2)

with c1:
    st.markdown(
        """
**What we could have used (and why it is weak here)**

- 📉 **Index volatility (σ of nifty)**  
  only tells how much the index moves, **ignores cross-section**.  
  high volatility can exist *with or without* herding.

- 🔗 **Average correlations**  
  need big correlation matrices and still do not directly show non-linear convergence.

- 📊 **CSSD (cross-sectional standard deviation)**  
  very sensitive to outliers; a few crazy stocks can distort it.

these measures mix up:

- “market is just volatile”  
- vs “market is moving like a herd”.
"""
    )

with c2:
    st.markdown(
        """
**Why CSAD fits this project**

- works well with **large cross-sections** (nifty + extended universe)  
- uses **absolute deviations**, less sensitive to extreme outliers  
- fits neatly into the **chang, cheng & khorana (2000)** non-linear model:
"""
    )
    st.latex(r"\text{CSAD}_t = \alpha + \gamma_1 |R_{m,t}| + \gamma_2 R_{m,t}^2 + \varepsilon_t")
    st.latex(r"\gamma_2 < 0 \;\Rightarrow\; \text{non-linear convergence (herding)}")

st.markdown(
    """
CSAD gives us:

- a **daily herding thermometer** (one number per day)  
- a clear test: if γ₂ is significantly negative, dispersion fails to grow with large |Rₘ| → **herding is present**.
"""
)

st.markdown("---")

# =====================================================
# 7. PLOTLY BAR – HERDING STRENGTH BY REGIME
# =====================================================

st.subheader("5️⃣ 📊 Which Regimes herd more than the baseline?")

st.write(
    "Bars show **extra herding intensity relative to the 1996–1999 baseline**, "
    "using −γ₂ only when γ₂ < 0. We summarise behaviour in each regime."
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
        "🧊 baseline (no herding)": "#60a5fa",   # blue
        "🐑 mild herding": "#f97373",            # mild red
        "🐃 strong herding": "#b91c1c",          # strong red
        "🧊 no herding": "#6b7280",              # fallback if it exists
    }
)



fig.update_traces(
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>HSI = %{y:.4f}<br>%{text}<extra></extra>"
)
fig.update_layout(
    title="Regime-wise non-linear herding intensity (csad γ₂ comparison)",
    xaxis_title="regime",
    yaxis_title="extra herding intensity vs baseline",
    legend_title="behaviour tag 🐃 / 🐑 / 🧊",
    bargap=0.25,
)

st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """
- 🧊 **Baseline (no herding)** → reference period 1996–1999  
- 🐃 **Strong herding** → crisis / mania regimes (e.g. GFC, covid)  
- 🐑 **Mild herding** → some convergence but still differentiated  
- 🧊 **No herding** → market behaves like independent investors.
"""
)

st.markdown("---")

# =====================================================
# 8. SUMMARY TABLE WITH EMOJIS + CONDITIONAL COLORS
# =====================================================

st.subheader("6️⃣ 📋 Regime-wise CSAD regression snapshot")

table_cols = ["regime_label", "n_obs", "mean_CSAD", "gamma2_Rm_sq", "herding_strength", "herding_label"]
table_df = summary_df[table_cols].copy()
table_df["mean_CSAD"] = table_df["mean_CSAD"].round(4)
table_df["gamma2_Rm_sq"] = table_df["gamma2_Rm_sq"].round(4)
table_df["herding_strength"] = table_df["herding_strength"].round(4)

# prettier column names
table_df = table_df.rename(
    columns={
        "regime_label": "regime",
        "n_obs": "trading days",
        "mean_CSAD": "Mean csad",
        "gamma2_Rm_sq": "γ₂ (Rm²)",
        "herding_strength": "herding strength (vs baseline)",
        "herding_label": "behaviour tag"
    }
)

def style_row(row):
    tag = row["behaviour tag"]
    if "baseline" in tag:
        color = "rgba(148, 163, 184, 0.18)"  # neutral
    elif tag.startswith("🐃"):
        color = "rgba(220, 38, 38, 0.18)"    # red-ish
    elif tag.startswith("🐑"):
        color = "rgba(234, 179, 8, 0.18)"    # amber
    else:
        color = "rgba(37, 99, 235, 0.18)"    # blue
    return [f"background-color: {color}"] * len(row)

styled = table_df.style.apply(style_row, axis=1)

with st.expander("📊  Detailed regime summary table", expanded=False):
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


st.markdown("---", unsafe_allow_html=True)

# Custom CSS targeting Streamlit buttons EXACTLY
st.markdown("---", unsafe_allow_html=True)

# Custom CSS targeting Streamlit buttons EXACTLY
st.markdown("---", unsafe_allow_html=True)

# Custom CSS targeting Streamlit buttons EXACTLY
st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #22c55e !important;
    color: white !important;

    padding: 22px 65px !important;
    border-radius: 22px !important;     /* << Rounded rectangle */
    
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

# Centered button + switch_page routing
st.markdown("<div class='centered-btn'>", unsafe_allow_html=True)
if st.button("📊 Next: Data & Methodology", key="go_data"):
    st.switch_page("pages/1_📊_Data_and_methodology.py")
st.markdown("</div>", unsafe_allow_html=True)

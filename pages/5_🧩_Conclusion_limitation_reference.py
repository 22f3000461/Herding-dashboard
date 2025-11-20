import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="🧩 Conclusion, limitations & references – Herding dashboard",
    page_icon="🧩",
    layout="wide"
)

st.markdown(
    """
    <style>
    .main > div { max-width: 1100px; margin-left:auto; margin-right:auto; }
    .markdown-text-container p,
    .markdown-text-container li { font-size:1.06rem; line-height:1.6; }
    h2, h3 { font-weight:700; }

    /* big centered finish button */
    .big-finish-btn button {
        display:inline-block;
        background-color:#4CAF50;
        padding:14px 32px;
        border-radius:10px;
        font-size:22px !important;
        font-weight:700 !important;
        color:white !important;
        border:none;
        box-shadow:0 4px 10px rgba(0,0,0,0.35);
        cursor:pointer;
    }
    .big-finish-wrapper {
        text-align:center;
        margin-top:30px;
        margin-bottom:10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧩 Conclusion, Suggestions, Limitations and References")
st.caption("Tying together the evidence from all Regimes")

@st.cache_data
def load_regime_summary(path: str):
    df = pd.read_csv(path)
    if "gamma2_Rm_sq" not in df.columns and "gamma2" in df.columns:
        df.rename(columns={"gamma2": "gamma2_Rm_sq"}, inplace=True)
    df["herding_strength"] = np.where(df["gamma2_Rm_sq"] < 0, -df["gamma2_Rm_sq"], 0.0)
    df["is_baseline"] = df["regime_label"].astype(str).str.contains("1996-1999")
    return df

summary_df = load_regime_summary("data/csad_regression_summary_all_regimes.csv")

# ---------------- 1. KEY FINDINGS ----------------
st.subheader("1️⃣ Key findings")

if not summary_df.empty:
    baseline = summary_df[summary_df["is_baseline"]].iloc[0]
    non_base = summary_df[~summary_df["is_baseline"]].copy()
    strongest = non_base.loc[non_base["herding_strength"].idxmax()]
    weakest = non_base.loc[non_base["herding_strength"].idxmin()]

    st.markdown(
        f"""
- baseline regime **1996–1999** behaves as a **reference, low-herding market**.  
- **{strongest['regime_label']}** shows the **strongest non-linear herding** (most negative γ₂).  
- **{weakest['regime_label']}** is the **most independent non-baseline regime**.  
- covid window and gfc period both show **episodic crowd behaviour** – dispersion collapses in large moves.
"""
    )

st.markdown("---")

# ---------------- 2. SUGGESTIONS ----------------
st.subheader("2️⃣ Suggestions / Implications")

st.markdown(
    """
**for regulators and exchanges**

- monitor **cross-sectional dispersion** along with volatility indices to detect crowding in real time.  
- during herding spikes, tighten **intraday risk controls** (margins, position limits, volatility filters).  

**for portfolio managers**

- treat **herding regimes** as distinct states: correlation structures and diversification benefits change.  
- stress testing should include scenarios where **dispersion collapses**, not only volatility spikes.  

**for retail investors**

- extremely unanimous narratives (everyone bullish / everyone bearish) often coincide with **low csad** →  
  these periods are **riskier than they look**.
"""
)

st.markdown("---")

# ---------------- 3. LIMITATIONS ----------------
st.subheader("3️⃣ Limitations of the study")

st.markdown(
    """
- uses **daily data** only – intraday herding is not captured.  
- csad focuses on **return convergence**; it does not separately model information vs sentiment shocks.  
- regime borders are **exogenously chosen** (based on macro events) rather than statistically estimated.  
- survivorship bias and changes in index composition may still matter, even after cleaning.
"""
)

st.markdown("---")

# ---------------- 4. EXTENSIONS ----------------
st.subheader("4️⃣ Possible Extensions")

st.markdown(
    """
- run **rolling csad regressions** to estimate a time-varying γ₂.  
- compare herding across **sectoral indices** (it, banks, small-caps vs large-caps).  
- combine csad with **order-flow or volume-based** herding measures.  
- compare Indian market herding with **other emerging markets** using the same framework.
"""
)

st.markdown("---")

# ---------------- 5. REFERENCES ----------------
st.subheader("5️⃣ References (core papers)")

st.markdown(
    """
- Chang, E. C., Cheng, J. W., & Khorana, A. (2000). **An examination of herd behavior in equity markets.** *Journal of Banking & Finance*.  
- Christie, W. G., & Huang, R. D. (1995). **Following the pied piper: Do individual returns herd around the market?** *Financial Analysts Journal*.  
- Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). **A theory of fads, fashion, custom, and cultural change as informational cascades.** *Journal of Political Economy*.  
- Relevant SEBI / RBI / NSE documents on market microstructure and volatility controls (for local context).
"""
)

st.markdown(
    """
this page summarises **what the dashboard has shown** and **where the csad-based analysis can be taken next**.
"""
)

st.markdown("---")

# ---------------- 6. FUNKY END BUTTON + EFFECTS ----------------
st.subheader("6️⃣ 🎉 End of the road (kind of)")

st.markdown(
    """
you’ve reached the last page of the dashboard.  
if you still expect a *next* page, hit the button and see what happens 👇
"""
)

st.markdown("<div class='big-finish-wrapper'>", unsafe_allow_html=True)
with st.container():
    # apply custom class to this button only
    finish_clicked = st.button("🚀 Next page (spoiler: there isn't one)", key="finish_btn", help="click to finish the journey", type="primary")
st.markdown("</div>", unsafe_allow_html=True)

if finish_clicked:
    st.success("😎 that’s it. you’ve officially reached the end of the herding dashboard. nice grind. ")
    st.balloons()
    st.snow()

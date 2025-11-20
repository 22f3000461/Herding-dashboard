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

    /* fancy finish button */
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
st.caption("wrapping up what we learned from watching markets lose their minds")

@st.cache_data
def load_regime_summary(path: str):
    df = pd.read_csv(path)
    # fixing column names because someone kept changing them
    if "gamma2_Rm_sq" not in df.columns and "gamma2" in df.columns:
        df.rename(columns={"gamma2": "gamma2_Rm_sq"}, inplace=True)
    df["herding_strength"] = np.where(df["gamma2_Rm_sq"] < 0, -df["gamma2_Rm_sq"], 0.0)
    df["is_baseline"] = df["regime_label"].astype(str).str.contains("1996-1999")
    return df

summary_df = load_regime_summary("data/csad_regression_summary_all_regimes.csv")

# ---------------- 1. WHAT WE FOUND ----------------
st.subheader("What the data actually told us")

if not summary_df.empty:
    baseline = summary_df[summary_df["is_baseline"]].iloc[0]
    non_base = summary_df[~summary_df["is_baseline"]].copy()
    strongest = non_base.loc[non_base["herding_strength"].idxmax()]
    weakest = non_base.loc[non_base["herding_strength"].idxmin()]

    st.markdown(
        f"""
- **1996–1999** is our chill baseline – markets doing their normal thing, low herding  
- **{strongest['regime_label']}** had people moving in lockstep the most (crazy negative γ₂)  
- **{weakest['regime_label']}** was where traders actually thought for themselves  
- both the GFC meltdown and covid circus showed clear signs of everyone running to the same exit
"""
    )

st.markdown("---")

# ---------------- 2. WHO CARES AND WHY ----------------
st.subheader("Why this matters (and what to do about it)")

st.markdown(
    """
**if you're a regulator or run an exchange:**

- watching just volatility isn't enough – track cross-sectional dispersion too  
- when CSAD tanks while everyone's trading, that's your red flag for a pile-on  
- maybe tighten margin requirements or circuit breakers when herding spikes  

**if you manage portfolios:**

- herding regimes break your usual diversification assumptions  
- when everyone crowds into the same trades, correlations go to 1 and your fancy risk models lie to you  
- stress tests need scenarios where dispersion collapses, not just vol explosions  

**if you're trading your own money:**

- when literally everyone agrees on a narrative (stocks only go up, or it's all going to zero), be scared  
- unanimous sentiment = low CSAD = you're probably late to the party  
- these periods look safe because "everyone's doing it" but they're actually sketchy as hell
"""
)

st.markdown("---")

# ---------------- 3. WHERE THIS FALLS SHORT ----------------
st.subheader("Stuff we didn't capture (because nothing's perfect)")

st.markdown(
    """
- we only looked at **daily closing prices** – all the intraday panic is invisible here  
- CSAD tells you when returns bunch up, but it can't tell you if that's rational info or pure panic  
- regime breaks are hand-picked based on what history books say, not what the data naturally clusters into  
- survivorship bias is still lurking somewhere – companies that died off aren't in this analysis  
- index composition changed over time, so we're not quite comparing apples to apples across decades
"""
)

st.markdown("---")

# ---------------- 4. WHERE TO GO NEXT ----------------
st.subheader("Ideas for taking this further")

st.markdown(
    """
- run the CSAD regression in **rolling windows** so you can see γ₂ evolving day by day  
- break it down by **sector** – tech probably herds way different than banks or pharma  
- mix in **order flow data** or actual trading volume to see who's doing the herding  
- compare Indian markets to other emerging markets using the same setup – is this unique or universal?  
- look at **social media sentiment** during the covid/IPO era to connect wsb chatter to dispersion drops
"""
)

st.markdown("---")

# ---------------- 5. WHERE I STOLE IDEAS FROM ----------------
st.subheader("Papers that did the heavy lifting first")

st.markdown(
    """
- **Chang, Cheng & Khorana (2000)** – the OG paper that made CSAD a thing for measuring herding  
- **Christie & Huang (1995)** – earlier approach looking at extreme market moves and return dispersion  
- **Bikhchandani, Hirshleifer & Welch (1992)** – theory behind why people follow the crowd even when it's dumb  
- various SEBI/RBI/NSE reports on how Indian markets actually work under the hood  

basically I'm standing on the shoulders of people smarter than me who figured this out years ago.
"""
)

st.markdown(
    """
so yeah, that's the story the data tells. markets aren't always rational, people follow each other off cliffs sometimes, and you can see it in the numbers if you look right.
"""
)

st.markdown("---")

# ---------------- 6. THE ACTUAL END ----------------
st.subheader("🎉 Congrats, you made it")

st.markdown(
    """
this is the last page. for real this time.  
there's no secret level. no bonus content. just this button that doesn't go anywhere ↓
"""
)

st.markdown("<div class='big-finish-wrapper'>", unsafe_allow_html=True)
with st.container():
    finish_clicked = st.button(
        "🚀 Click for next page (spoiler: nope)", 
        key="finish_btn", 
        help="I literally just told you there isn't one", 
        type="primary"
    )
st.markdown("</div>", unsafe_allow_html=True)

if finish_clicked:
    st.success("🎊 told you so. you've seen everything. now go outside or something.")
    st.balloons()
    st.snow()
    st.markdown(
        """
        ---
        *thanks for actually reading through this whole thing instead of just skipping to the conclusion like a normal person would*
        """
    )
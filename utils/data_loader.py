# utils/data_loader.py

import os
from typing import Tuple, Dict

import pandas as pd
import streamlit as st
from stqdm import stqdm

# --------------------------------------------------
# PATHS
# --------------------------------------------------

# this file is in DASHBOARD/utils/data_loader.py
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)          # -> DASHBOARD
DATA_DIR = os.path.join(_PROJECT_ROOT, "data")      # -> DASHBOARD/data


# --------------------------------------------------
# REGIME CONFIG
# (file names MUST match exactly what is in /data)
# --------------------------------------------------

REGIMES: Dict[str, Dict[str, str]] = {
    "1996–1999  🧱  Baseline": {
        "summary_label": "1996-1999",
        "csad":     "csad_1996_1999.csv",
        "prices":   "prices_baseline_1996_1999.csv",
        "returns":  "returns_baseline_1996_1999.csv",
        "universe": "baseline_universe_1996_1999.csv",
    },
    "1999–2007  📈  Pre-GFC Boom": {
        "summary_label": "1999-2007",
        "csad":     "csad_1999_2007.csv",
        "prices":   "prices_1999_2007.csv",
        "returns":  "returns_1999_2007.csv",
        "universe": "universe_1999_2007.csv",
    },
    "2007–2009  💥  GFC Crisis": {
        "summary_label": "2007-2009",
        "csad":     "csad_2007_2009.csv",
        "prices":   "prices_2007_2009.csv",
        "returns":  "returns_2007_2009.csv",
        "universe": "universe_2007_2009.csv",
    },
    "2015–2024  📱  Modern Era": {
        "summary_label": "2015-2024",
        "csad":     "csad_2015_2024.csv",
        "prices":   "prices_2015_2024.csv",
        "returns":  "returns_2015_2024.csv",
        "universe": "universe_2015_2024.csv",
    },
    "2020–2022  😷  Covid + IPO Mania": {
        "summary_label": "2020-2022",
        "csad":     "csad_2020_2022.csv",
        "prices":   "prices_2020_2022.csv",
        "returns":  "returns_2020_2022.csv",
        "universe": "universe_2020_2022.csv",
    },
}

# convenient list for dropdowns in app.py
REGIME_OPTIONS = list(REGIMES.keys())


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def _load_csv(filename: str) -> pd.DataFrame:
    """Internal: load a CSV from DATA_DIR and parse date if present."""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        st.error(f"File not found: {path}")
        st.stop()

    df = pd.read_csv(path)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date")

    return df


# --------------------------------------------------
# PUBLIC FUNCTIONS
# --------------------------------------------------

@st.cache_data
def load_summary() -> Tuple[pd.DataFrame | None, str]:
    """
    Load regression summary for all regimes.
    Returns (df, path). df is None if file does not exist.
    """
    filename = "csad_regression_summary_all_regimes.csv"
    path = os.path.join(DATA_DIR, filename)

    if os.path.exists(path):
        df = pd.read_csv(path)
        return df, path
    else:
        return None, path


@st.cache_data
def load_regime_data(regime_display_name: str) -> Tuple[pd.DataFrame, pd.DataFrame,
                                                       pd.DataFrame, pd.DataFrame]:
    """
    Load csad, prices, returns, universe for a selected regime.

    Returns:
        csad_df, prices_df, returns_df, universe_df
    """
    if regime_display_name not in REGIMES:
        st.error(f"Unknown regime key: {regime_display_name}")
        st.stop()

    cfg = REGIMES[regime_display_name]

    # nice progress bar when everything loads first time
    out = {}
    for key in stqdm(["csad", "prices", "returns", "universe"], desc="Loading regime data"):
        out[key] = _load_csv(cfg[key])

    return out["csad"], out["prices"], out["returns"], out["universe"]

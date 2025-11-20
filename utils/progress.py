# utils/progress.py

import streamlit as st

# adjust if you add more pages later
TOTAL_STEPS = 4   # e.g. Home, Data, Regime, Covid/Conclusion


def progress_slider(page_step: int):
    """
    page_step: integer for current page (1..TOTAL_STEPS).
    Keeps max visited page in session_state and shows a disabled slider.
    """
    if "progress_step" not in st.session_state:
        st.session_state["progress_step"] = page_step

    st.session_state["progress_step"] = max(
        st.session_state["progress_step"],
        page_step,
    )

    completed = st.session_state["progress_step"]
    pct = int(completed / TOTAL_STEPS * 100)

    st.slider(
        "Dashboard completion",
        min_value=1,
        max_value=TOTAL_STEPS,
        value=completed,
        step=1,
        disabled=True,
    )
    st.caption(f"You have completed about {pct}% of the dashboard.")

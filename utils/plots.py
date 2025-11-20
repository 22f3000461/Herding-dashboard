# utils/plots.py

import plotly.express as px
import pandas as pd


def price_time_series(prices_df: pd.DataFrame, title: str):
    """
    prices_df must have columns: date, index_level (or any numeric column you pass as y_col)
    """
    fig = px.line(
        prices_df,
        x="date",
        y="index_level",
        title=title,
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title="Date",
        yaxis_title="Index level",
    )
    return fig


def csad_time_series(csad_df: pd.DataFrame, title: str):
    fig = px.line(
        csad_df,
        x="date",
        y="CSAD",
        title=title,
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title="Date",
        yaxis_title="CSAD",
    )
    return fig


def csad_vs_abs_rm(csad_df: pd.DataFrame, title: str):
    """
    Scatter CSAD vs |Rm| with quadratic fit drawn on top.
    Requires columns: abs_Rm, CSAD.
    """
    fig = px.scatter(
        csad_df,
        x="abs_Rm",
        y="CSAD",
        opacity=0.5,
        title=title,
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title="|R_m|",
        yaxis_title="CSAD",
    )
    return fig

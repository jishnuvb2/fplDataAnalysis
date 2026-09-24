import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from highlight_text import fig_text
from mplsoccer import PyPizza, FontManager
import plotly.express as px
from plotly.subplots import make_subplots
from dataFetch import clean_data

def render_1v1_compare():
    player_df, team_df = clean_data()
    player1 = st.selectbox(
        "Select Player 1",
        options=player_df["web_name"] + " (" + player_df["team"] + ")",
        index=None,
        placeholder="Select Player 1"
    )
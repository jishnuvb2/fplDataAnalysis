import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from highlight_text import fig_text
from mplsoccer import PyPizza, FontManager
import plotly.express as px
from plotly.subplots import make_subplots
from dataFetch import clean_data

def get_player(df, player):
    web_name, team_bracket = player.split(" (")
    team = team_bracket.rstrip(")")
    web_name = web_name.strip()
    team = team.strip()

    mask = df["web_name"] == web_name
    if team:
        mask &= df["team"] == team
    return df[mask]



def render_1v1_compare():
    player_df, team_df = clean_data()
    player1 = st.selectbox(
        "Select Player 1",
        options=player_df["web_name"] + " (" + player_df["team"] + ")",
        index=None,
        placeholder="Select Player 1"
    )

    player2 = st.selectbox(
        "Select Player 2",
        options=player_df["web_name"] + " (" + player_df["team"] + ")",
        index=None,
        placeholder="Select Player 2"
    )

    both_selected = player1 is not None and player2 is not None
    if st.button("Generate Chart", disabled=not both_selected):
        player1_clean = get_player(player_df, player1)
        player2_clean = get_player(player_df, player2)
        st.success(f"Generating comparison chart for {player1_clean} vs {player2_clean}!")

    

    
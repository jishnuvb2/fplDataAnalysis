import streamlit as st
from  dataFetch import clean_data
from components import render_1v1_compare, render_charts
from styles import style

st.set_page_config(
    page_title="FPL Data Analysis",
    layout="wide",  # This strips out the large left/right whitespace margins
)


st.html(style)
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

st.sidebar.title("Contents")
st.sidebar.write("----")

if st.sidebar.button("Home", use_container_width=True):
    st.session_state.current_page = "Home"

if st.sidebar.button("Charts", use_container_width=True):
    st.session_state.current_page = "Charts"

if st.sidebar.button("Team Analysis", use_container_width=True):
    st.session_state.current_page = "Team Analysis"

if st.sidebar.button("1v1 Compare", use_container_width=True):
    st.session_state.current_page = "1v1 Compare"

page = st.session_state.current_page
player_df, team_df = clean_data()
st.session_state.player_df = player_df
st.session_state.team_df = team_df

if page == "Home":
    st.title("Home Page")

elif page == "Charts":
    st.title("Charts Page")
    render_charts()

elif page == "Team Analysis":
    st.title("Team analysis")

elif page == "1v1 Compare":
    render_1v1_compare()
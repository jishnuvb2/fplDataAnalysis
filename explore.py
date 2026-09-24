import streamlit as st
from  dataFetch import clean_data

st.title("FPL Live Dashboard")
st.write("App is successfully deployed and running live!")

if st.button("Refresh Data"):
    # below code runs only if this button has been clicked
    with st.spinner("Please wait while connecting to FPL API"):
        player_df, team_df = clean_data()
        st.metric(label="No of Teams", value=len(team_df))

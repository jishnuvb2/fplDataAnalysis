import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from highlight_text import fig_text
from mplsoccer import PyPizza, FontManager
import plotly.express as px
from plotly.subplots import make_subplots
from dataFetch import clean_data
from config import metrics_definition
#********* Styling ******

font_normal = FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/'
                          'src/hinted/Roboto-Regular.ttf')
font_italic = FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/'
                          'src/hinted/Roboto-Italic.ttf')
font_bold = FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/'
                        'RobotoSlab[wght].ttf')

#************** 1v1 Compare *******************

# function that returns the mask for the selected player
def get_player(df, player):
    web_name, team_bracket = player.split(" (")
    team = team_bracket.rstrip(")")
    web_name = web_name.strip()
    team = team.strip()

    mask = df["web_name"] == web_name
    if team:
        mask &= df["team"] == team
    return df[mask]

# function that builds the pizza plot
def returnPizzaContainer(player_df, player1_df, player2_df, metric):
    params = metrics_definition[metric]
    min_range = player_df[params].min().tolist()
    max_range = player_df[params].max().tolist()
    values1 = player1_df[params].values.flatten().tolist()
    values2 = player2_df[params].values.flatten().tolist()
    baker = PyPizza(
        params=params,                  # list of parameters
        min_range=min_range,
        max_range=max_range,
        background_color="#EBEBE9",     # background color
        straight_line_color="#222222",  # color for straight lines
        straight_line_lw=1,             # linewidth for straight lines
        last_circle_lw=1,               # linewidth of last circle
        last_circle_color="#222222",    # color of last circle
        other_circle_ls="-.",           # linestyle for other circles
        other_circle_lw=1               # linewidth for other circles
    )
    fig, ax = baker.make_pizza(
        values1,                     # list of values
        compare_values=values2,    # comparison values
        figsize=(8, 8),             # adjust figsize according to your need
        kwargs_slices=dict(
            facecolor="#1A78CF", edgecolor="#222222",
            zorder=2, linewidth=1
        ),                          # values to be used when plotting slices
        kwargs_compare=dict(
            facecolor="#FF9300", edgecolor="#222222",
            zorder=2, linewidth=1,
        ),
        kwargs_params=dict(
            color="#000000", fontsize=12,
            fontproperties=font_normal.prop, va="center"
        ),                          # values to be used when adding parameter
        kwargs_values=dict(
            color="#000000", fontsize=12,
            fontproperties=font_normal.prop, zorder=3,
            bbox=dict(
                edgecolor="#000000", facecolor="cornflowerblue",
                boxstyle="round,pad=0.2", lw=1
            )
        ),                          # values to be used when adding parameter-values labels
        kwargs_compare_values=dict(
            color="#000000", fontsize=12, fontproperties=font_normal.prop, zorder=3,
            bbox=dict(edgecolor="#000000", facecolor="#FF9300", boxstyle="round,pad=0.2", lw=1)
        ),                          # values to be used when adding parameter-values labels
    )

    p1_name = player1_df["web_name"].iloc[0]
    p2_name = player2_df["web_name"].iloc[0]

    # add title
    fig_text(
        0.515, 0.99, f"<{p1_name}> vs <{p2_name}>", size=17, fig=fig,
        highlight_textprops=[{"color": '#1A78CF'}, {"color": '#EE8900'}],
        ha="center", fontproperties=font_bold.prop, color="#000000"
    )

    return fig



def render_1v1_compare():
    st.title("1v1 Player Comparision")
    player_df = st.session_state.player_df
    metric_list = ["Overall", "Attack", "Defence", "Captaincy"]
    display_options = player_df["web_name"] + " (" + player_df["team"] + ")"

    col1, col2, col3 = st.columns(3)

    with col1:
        player1 = st.selectbox(
            "Select Player 1",
            options=display_options,
            index=None,
            placeholder="Select Player 1",
        )

    with col2:
        player2 = st.selectbox(
            "Select Player 2",
            options=display_options,
            index=None,
            placeholder="Select Player 2",
        )

    with col3:
        metric = st.selectbox(
            "Select Comparison Metric", options=metric_list, index=None
        )

    both_selected = player1 is not None and player2 is not None and metric is not None    
    if st.button("Generate Chart", disabled=not both_selected):
        player1_df = get_player(player_df, player1)
        player2_df = get_player(player_df, player2)
        fig = returnPizzaContainer(player_df, player1_df, player2_df, metric)
        st.pyplot(fig)


#****************************Charts Page*********************************************

def draw_chart(df, x_axis, y_axis, color, hover_fields):
    fig = px.scatter(
        df,
        x=x_axis,
        y=y_axis,
        color=color,
        hover_name= "web_name",
        hover_data= hover_fields,
        title= f"{x_axis} vs {y_axis}",
    )

    fig.update_layout(
    title_x=0.5,  # Centers the title text
    title_font=dict(size=20, family="Roboto, sans-serif"),
    )
    return fig

def render_charts():
    # Create two columns with a 3:7 ratio (30% and 70%)
    col1, col2 = st.columns([3, 7])
    player_df = st.session_state.player_df
    team_df = st.session_state.team_df
    with col1:
        # filter section
        position = st.multiselect(
            "Filter Player Positions",
            ["GKP", "DEF", "MID", "FWD"],
            default=["GKP", "DEF", "MID", "FWD"],
            wrap=True
        )

        team = st.multiselect(
            "Choose teams or select all",
            team_df["short_name"].unique(),
            default=[],
            wrap=True
        )

        price_range = st.slider(
            "Set Price Range",
            0.0,20.0,(4.0, 16.0)
        )

    filters_selected = position is not None and team is not None and price_range is not None

    with col2:
        # the actual chart goes here
        if filters_selected:
            mask_position = player_df["element_type"].isin(position)
            mask_team = player_df["team"].isin(team)
            mask_price = (player_df["now_cost"] >= price_range[0]) & (
                player_df["now_cost"] <= price_range[1]
            )
            combined_mask = mask_position & mask_team & mask_price
            filtered_players = player_df[combined_mask]

        col2_1, col2_2 = st.columns(2)
        with col2_1:
            # get the x and y axis
            x_axis = st.selectbox(
                "Choose your X Axis",
                options = player_df.columns.to_list(),
                index=None 
            )

            color = st.selectbox(
                "Color By",
                options= player_df.columns.to_list(),
                index=None,
                placeholder= "Segregate the output by this column"
            )

        with col2_2:
            y_axis = st.selectbox(
                "Choose your Y Axis",
                options = player_df.columns.to_list(),
                index=None 
            )

            

            hover_fields = st.multiselect(
                "Chose data to appear on hover",
                options=player_df.columns.to_list(),
                default=["now_cost", "selected_by_percent"],
                wrap=True
            )

        axis_selected = x_axis is not None and y_axis is not None and color is not None and hover_fields is not None

    if st.button("Generate Chart", disabled=not axis_selected or not filters_selected):
        fig = draw_chart(filtered_players, x_axis, y_axis, color, hover_fields)
        st.plotly_chart(fig, use_container_width=True)

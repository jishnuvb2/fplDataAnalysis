# this file is used to import the player data and team data
from config import GAMEWEEK, MANAGER_ID
import pandas as pd
import requests
import numpy as np

# function to fetch team data from FPL website
def fetch_team_data():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    res = requests.get(url).json()
    df = pd.DataFrame(res['teams'])
    df.columns

    team_cols = [
        'id',
        'short_name',
        'position',
        'played'
    ]
    team_df = df[team_cols]
    team_df.head()
    # Fix slice warning by making an explicit copy
    team_df = df[team_cols].copy()

    # Fetch fixture data
    fixtures_url = "https://fantasy.premierleague.com/api/fixtures/"
    fixtures_data = requests.get(fixtures_url).json()
    fixtures_df = pd.DataFrame(fixtures_data)

    # Filter for unplayed upcoming fixtures
    upcoming_fixtures = fixtures_df[fixtures_df['finished'] == False].copy()

    # Create lookup mapping for team names/short names
    team_id_to_short = dict(zip(df['id'], df['short_name']))

    # Build dictionary to store next 5 fixtures per team
    team_next_5 = {team_id: [] for team_id in df['id']}

    # Iterate through upcoming matches and store home/away fixture details
    for _, fix in upcoming_fixtures.iterrows():
        h_id, a_id = fix['team_h'], fix['team_a']
        h_fdr, a_fdr = fix['team_h_difficulty'], fix['team_a_difficulty']

        if len(team_next_5[h_id]) < 5:
            team_next_5[h_id].append((f"{team_id_to_short[a_id]}(H) ({h_fdr})", h_fdr))

        if len(team_next_5[a_id]) < 5:
            team_next_5[a_id].append((f"{team_id_to_short[h_id]}(A) ({a_fdr})", a_fdr))

    # Extract F1-F5 strings and calculate cumulative difficulty score safely using .loc
    for i in range(5):
        team_df.loc[:, f'F{i+1}'] = team_df['id'].map(lambda tid: team_next_5[tid][i][0] if len(team_next_5[tid]) > i else None)

    team_df.loc[:, 'fdr_sum_next_5'] = team_df['id'].map(lambda tid: sum(fix[1] for fix in team_next_5[tid][:5]))

    return team_df


def fetch_player_data():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    res = requests.get(url).json()
    df = pd.DataFrame(res['elements'])
    cols_retain = [
        'web_name', 'element_type', 'team', 'now_cost',
        'selected_by_percent', 'total_points', 'event_points', 'points_per_game',
        'form', 'transfers_in_event',
        'transfers_out_event', 'minutes', 'starts', 'starts_per_90',
        'goals_scored', 'assists', 'expected_goals', 'expected_assists',
        'expected_goals_per_90', 'expected_goal_involvements_per_90', 'clean_sheets', 'clean_sheets_per_90',
        'goals_conceded', 'own_goals', 'defensive_contribution', 'bonus',
        'bps', 'influence', 'creativity', 'threat', 'ict_index', 'id', 'defensive_contribution_per_90',
        'expected_goals_conceded_per_90', 'expected_goals_conceded', 'expected_goal_involvements'
    ]

    player_df = df[cols_retain].copy()
    pos_map = {
        1: 'GKP',
        2: 'DEF',
        3: 'MID',
        4: 'FWD'
    }

    player_df['element_type'] = player_df['element_type'].map(pos_map)
    player_df['now_cost'] = player_df['now_cost']/10


    cols_to_convert = [
        'selected_by_percent', 'points_per_game', 'form', 'ep_this', 'ep_next',
        'expected_goals', 'expected_assists', 'influence', 'creativity', 'threat','expected_goals_conceded',
        'expected_goal_involvements'
    ]

    for col in cols_to_convert:
        if col in player_df.columns:
            player_df[col] = (
                player_df[col]
                .astype(str)
                .str.replace(',', '', regex=False)
                .str.strip()
                .replace({'': '0', 'nan': '0', 'None': '0'})
            )
            # Step 2: Convert directly to float
            player_df[col] = pd.to_numeric(player_df[col], errors='coerce')
    
    return player_df

def clean_data():
    team_df = fetch_team_data()
    player_df = fetch_player_data()
    team_id_to_short = dict(zip(team_df['id'], team_df['short_name']))
    player_df['team']= player_df['team'].map(team_id_to_short)
    # get the expected goals against for a team.
    ttdf = player_df.groupby('team')['expected_goals'].sum().reset_index()
    # 1. Filter out only the goalkeepers (element_type 1) from your main data
    gk_df = player_df[player_df["element_type"] == "GKP"]

    # 2. Group goalkeepers by team and sum up their 'expected_goals_conceded'
    xga_df = (
        gk_df.groupby("team")["expected_goals_conceded"]
        .sum()
        .reset_index()
    )
    # 4. Merge this new data directly into your existing ttdf
    ttdf = pd.merge(ttdf, xga_df, on="team", how="left")

    ttdf = ttdf.rename(columns={'expected_goals': 'xgTeam', 'expected_goals_conceded': 'xgaTeam'})
    team_df = pd.merge(team_df, ttdf, left_on="short_name", right_on="team", how="left")

    # bring in the next 5 fixtures FDR Rating.
    player_df = player_df.merge(
        team_df[["short_name", "F1", "F2", "F3", "F4", "F5", "fdr_sum_next_5", "xgTeam", "xgaTeam"]],
        left_on = "team",
        right_on = "short_name",
        how="left"
        ).drop(columns=["short_name"])

    # get the player contribution values
    player_df["XGcontribution"] = player_df['expected_goals'] / player_df['xgTeam']
    player_df["XAcontribution"] = player_df['expected_assists'] / player_df['xgTeam']

    # setting my team
    url = f"https://fantasy.premierleague.com/api/entry/{MANAGER_ID}/event/{GAMEWEEK}/picks/"
    response = requests.get(url).json()
    # Returns player element IDs, position order, and multipliers (1 for starter, 2 for captain)
    my_player_ids = [pick['element'] for pick in response['picks']]

    player_df["goal_involvements"] = player_df["goals_scored"] + player_df["assists"]
    player_df["in_my_team"] = False
    # Flag squad membership
    player_df["in_my_team"] = player_df["id"].isin(my_player_ids)

    # setting up the metrics configuration

    metrics_config = {
        'rank_killer' : {
            'GKP' : (player_df['selected_by_percent'] > 25.0) & (~player_df['in_my_team']) & (player_df['points_per_game'] > 5.0),
            'DEF' : (player_df['selected_by_percent'] > 25.0) & (~player_df['in_my_team']) & (player_df['points_per_game'] > 5.0),
            'MID' : (player_df['selected_by_percent'] > 25.0) & (~player_df['in_my_team']) & (player_df['points_per_game'] > 5.0),
            'FWD' : (player_df['selected_by_percent'] > 25.0) & (~player_df['in_my_team']) & (player_df['points_per_game'] > 5.0)
        },
        'differential': {
            'GKP' : (player_df['selected_by_percent'] < 10.0) & (player_df['points_per_game'] > 4.0),
            'DEF' : (player_df['selected_by_percent'] < 10.0) & (player_df['defensive_contribution_per_90'] > 8.0)
                    & (player_df['points_per_game'] > 4.5) & (player_df['expected_goals_conceded_per_90'] < 1.5),
            'MID': (player_df['selected_by_percent'] < 10.0) & (player_df['expected_goal_involvements_per_90'] > 0.5)
                    & (player_df['points_per_game'] > 5.0),
            'FWD':  (player_df['selected_by_percent'] < 10.0) & (player_df['expected_goal_involvements_per_90'] > 0.5)
        },
        'overpaid':{
            'GKP' : (player_df['now_cost'] > 5.0) & (player_df['points_per_game'] < 2.5),
            'DEF' : (player_df['now_cost'] >= 5.0) & (player_df['points_per_game'] <= 3.0),
            'MID' : (player_df['now_cost'] >= 7.0) & (player_df['points_per_game'] <= 3.5),
            'FWD' : (player_df['now_cost'] >= 7.0) & (player_df['points_per_game'] <= 3.5)
        },
        'value_pick' : {
            'GKP' : (player_df['now_cost'] <= 4.7) & (player_df['points_per_game'] >= 4.0),
            'DEF' : (player_df['now_cost'] <= 4.7) & (player_df['points_per_game'] >= 4.0),
            'MID' : (player_df['now_cost'] <= 6.5) & (player_df['points_per_game'] >= 5.0),
            'FWD' : (player_df['now_cost'] <= 6.5) & (player_df['points_per_game'] >= 5.0),
        },
        'enabler': {
            'GKP' : (player_df['now_cost'] < 4.5) & (player_df['starts_per_90'] > 0.7),
            'DEF' : (player_df['now_cost'] < 4.5) & (player_df['starts_per_90'] > 0.5) & (player_df['points_per_game'] >= 3.5),
            'MID' : (player_df['now_cost'] <= 5.0) & (player_df['starts_per_90'] > 0.5) & (player_df['points_per_game'] >= 3.5),
            'FWD' : (player_df['now_cost'] <= 5.5) & (player_df['starts_per_90'] > 0.5) & (player_df['points_per_game'] >= 3.5)
        },
        'unsustainable': {
            'GKP': (player_df['points_per_game'] > 3.0) & (player_df['expected_goals_conceded_per_90'] > 1.0),
            'DEF': (player_df['points_per_game'] >= 4.5) & (player_df['expected_goals_conceded_per_90'] > 1.0)
                & (player_df['defensive_contribution_per_90'] < 8.0),
            'MID': (player_df['points_per_game'] >= 4.5) & (player_df['expected_goal_involvements_per_90'] <= 0.5)
                & (player_df['defensive_contribution_per_90'] < 9.0),
            'FWD': (player_df['points_per_game'] >= 4.5) & (player_df['expected_goal_involvements_per_90'] <= 0.5)
        },
        'promise': {
            'GKP' : (player_df['points_per_game'] <= 4.0) & (player_df['expected_goals_conceded_per_90'] <= 1.0),
            'DEF' : (player_df['points_per_game'] <= 4.0) & (player_df['defensive_contribution_per_90'] >= 8.0)
                & (player_df['expected_goals_conceded_per_90'] < 0.9) & (player_df['starts_per_90'] > 0.5),
            'MID' : (player_df['points_per_game'] <= 4.0) & ((player_df['expected_goal_involvements_per_90'] > 0.5)
                | (player_df['defensive_contribution_per_90'] >= 10.0)) & (player_df['starts_per_90'] > 0.5),
            'FWD': (player_df['points_per_game'] <= 4.0) & (player_df['expected_goal_involvements_per_90'] > 0.5)
                    & (player_df['starts_per_90'] > 0.5)
        },
        'must_have': {
            'GKP' : (player_df['points_per_game'] > 4.0),
            'DEF' : (player_df['points_per_game'] > 5.0),
            'MID' : (player_df['points_per_game'] > 5.0),
            'FWD' : (player_df['points_per_game'] > 5.0)
        },
        'form_player': {
            'GKP' : (player_df['form'] > 5.0),
            'DEF' : (player_df['form'] > 5.0),
            'MID' : (player_df['form'] > 5.0),
            'FWD' : (player_df['form'] > 5.0)
        },
        'bench_fodder': {
            'GKP' : (player_df['now_cost'] <= 4.3) & (player_df['starts_per_90'] > 0.7),
            'DEF' : (player_df['now_cost'] <=4.3) & (player_df['starts_per_90'] > 0.5) & (player_df['points_per_game'] >= 3.0),
            'MID' : (player_df['now_cost'] <= 5.0) & (player_df['starts_per_90'] > 0.5) & (player_df['points_per_game'] >= 3.0),
            'FWD' : (player_df['now_cost'] <= 4.5) & (player_df['starts_per_90'] > 0.5) & (player_df['points_per_game'] >= 2.5)
        }
    }

    # 1. Loop through each metric and its positional rules
    for metric_name, pos_rules in metrics_config.items():
        # Initialize the new column to False
        player_df[metric_name] = False

        # Apply conditions filtered by element_type
        for pos, mask in pos_rules.items():
            player_df.loc[(player_df['element_type'] == pos) & mask, metric_name] = True

        player_df['defcon_pos_rank'] = (
        player_df.groupby('element_type')['defensive_contribution']
        .rank(pct=True)
    )

    if 'F1' in player_df.columns:
        player_df["opp1"] = player_df["F1"].str.extract(r"^([A-Z]+)")
        player_df["opp2"] = player_df["F2"].str.extract(r"^([A-Z]+)")
        player_df["opp3"] = player_df["F3"].str.extract(r"^([A-Z]+)")
        player_df["opp4"] = player_df["F4"].str.extract(r"^([A-Z]+)")
        player_df["opp5"] = player_df["F5"].str.extract(r"^([A-Z]+)")

        player_df.drop(columns=["F2", "F3", "F4", "F5"], inplace=True)
    else:
        print("Warning: F1-F5 columns not found in player_df. Assuming opponent columns (opp1-opp5) were already created or will be handled elsewhere.")

    # Merge xgaTeam for each opponent, correcting the renaming issue
    # The existing xgaTeam (player's team) will remain named xgaTeam.
    # The incoming xgaTeam (opponent's) will be suffixed then renamed.

    att_weight = np.where(player_df['element_type'] == 'DEF', 4.2,
                np.where(player_df['element_type'] == 'MID', 4.0,
                np.where(player_df['element_type'] == 'FWD', 3.8, 3.0)))

    # Defensive Weight (W_DEF): DEF/GKP=4.0, MID/FWD=0.0 (zeroed out to prevent mid clean-sheet inflation)
    def_weight = np.where(player_df['element_type'].isin(['DEF', 'GKP']), 4.0, 0.0)

    for i in range(1, 6):
        # Merge team_df to get the opponent's xgaTeam
        # Use suffixes to prevent renaming player_df's existing 'xgaTeam'
        # The incoming 'short_name' will be suffixed '_temp_sn'
        # The incoming 'xgaTeam' will be suffixed '_temp_xga'
        player_df = player_df.merge(team_df[['short_name', 'xgaTeam', 'xgTeam']],
                                    left_on=f'opp{i}', right_on='short_name',
                                    how='left',
                                    suffixes=('', f'_temp_opp{i}'))

        # Rename the opponent's xgaTeam column to the desired format (e.g., 'xga_opp1')
        player_df.rename(columns={f'xgaTeam_temp_opp{i}': f'xga_opp{i}', f'xgTeam_temp_opp{i}' : f'xg_opp{i}'}, inplace=True)

        # Drop the temporary short_name column from the merge
        player_df.drop(columns=[f'short_name_temp_opp{i}'], errors='ignore', inplace=True)

    # Calculate eGI values
    for i in range(1, 6):
        # 1. Expected Team Goals for match i using your GAMEWEEK baseline
        etxg = (player_df['xgTeam'] + player_df[f'xga_opp{i}']) / (2 * GAMEWEEK)
        etxga = (player_df[f'xg_opp{i}'] + player_df['xgaTeam']) / (2 * GAMEWEEK)

        # 2. Separate eG and eA to maintain proper share scaling
        eG = player_df['XGcontribution'] * etxg
        eA = player_df['XAcontribution'] * (etxg * 0.7)
        player_df[f'match_{i}_xga'] = etxga
        player_df[f'match_{i}_defScore'] = player_df['defcon_pos_rank']/etxga
        # 3. Store match eGI
        player_df[f'match_{i}_eGI'] = eG + eA
        xp_underlying = 2.0 + (player_df[f'match_{i}_eGI'] * att_weight) + (player_df[f'match_{i}_defScore'] * def_weight)
        player_df[f'match_{i}_xPts'] = (0.60 * xp_underlying) + (0.40 * player_df['form'])

    # 4. Total 5-game rolling eGI
    player_df['eGI_5'] = player_df[[f'match_{i}_eGI' for i in range(1, 6)]].sum(axis=1)
    player_df['xgA_5'] = player_df[[f'match_{i}_xga' for i in range(1, 6)]].sum(axis=1)
    player_df['ds_5'] = player_df[[f'match_{i}_defScore' for i in range(1, 6)]].sum(axis=1)
    player_df['xpts_5'] = player_df[[f'match_{i}_xPts' for i in range(1, 6)]].sum(axis=1)
    player_df.drop(columns=['short_name'], inplace=True)

    return player_df, team_df



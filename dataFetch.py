# this file is used to import the player data and team data
from config import GAMEWEEK, MANAGER_ID, fpl_team_map
import pandas as pd
import requests
import numpy as np
from understatapi import UnderstatClient

""""
def fetch_understat():
    with UnderstatClient() as client:
        # 1. Target the EPL league layer for the 2026/27 season
        # 2. Call get_team_data() to pull the master dictionary
        leagues_data = client.league(league="EPL").get_team_data(season="2026")

        all_matches = []
        for team_id, team_info in leagues_data.items():
            team_name = team_info['title']
            understat_id = team_info['id']
            
            for match in team_info['history']:
                ppda_dict = match.get('ppda', {})
                ppda_allowed_dict = match.get('ppda_allowed', {})
                
                all_matches.append({
                    'Team_ID': understat_id,
                    'Team': team_name,
                    
                    # Counting match outcomes
                    'Goals_Scored': int(match.get('scored', 0)),
                    'Goals_Conceded': int(match.get('missed', 0)),
                    'Points': int(match.get('pts', 0)),
                    'Wins': int(match.get('wins', 0)),
                    'Draws': int(match.get('draws', 0)),
                    'Losses': int(match.get('loses', 0)),
                    
                    # Underlying Performance Analytics
                    'xG_Created': float(match.get('xG', 0)),
                    'xG_Conceded': float(match.get('xGA', 0)),
                    'npxG_Created': float(match.get('npxG', 0)),
                    'npxG_Conceded': float(match.get('npxGA', 0)),
                    'npxG_Difference': float(match.get('npxGD', 0)),
                    'Expected_Points': float(match.get('xpts', 0)),
                    
                    # Progression Metrics
                    'Deep_Passes_Completed': int(match.get('deep', 0)),
                    'Deep_Passes_Allowed': int(match.get('deep_allowed', 0)),
                    
                    # PPDA raw values
                    'PPDA_Attacking_Passes': int(ppda_dict.get('att', 0)),
                    'PPDA_Defensive_Actions': int(ppda_dict.get('def', 0)),
                    'PPDA_Allowed_Att': int(ppda_allowed_dict.get('att', 0)),
                    'PPDA_Allowed_Def': int(ppda_allowed_dict.get('def', 0))
                })

        df_matches = pd.DataFrame(all_matches)

        # 2. Season-level aggregation grouped by Team
        team_aggregates = df_matches.groupby(['Team_ID', 'Team']).agg({
            'Goals_Scored': 'sum',
            'Goals_Conceded': 'sum',
            'Points': 'sum',
            'Wins': 'sum',
            'Draws': 'sum',
            'Losses': 'sum',
            'xG_Created': 'sum',
            'xG_Conceded': 'sum',
            'npxG_Created': 'sum',
            'npxG_Conceded': 'sum',
            'npxG_Difference': 'sum',
            'Expected_Points': 'sum',
            'Deep_Passes_Completed': 'sum',
            'Deep_Passes_Allowed': 'sum',
            'PPDA_Attacking_Passes': 'sum',
            'PPDA_Defensive_Actions': 'sum',
            'PPDA_Allowed_Att': 'sum',
            'PPDA_Allowed_Def': 'sum'
        }).reset_index()

        # 3. Calculate seasonal derived ratios
        team_aggregates['PPDA_Coeff'] = team_aggregates['PPDA_Attacking_Passes'] / team_aggregates['PPDA_Defensive_Actions']
        team_aggregates['PPDA_Allowed_Coeff'] = team_aggregates['PPDA_Allowed_Att'] / team_aggregates['PPDA_Allowed_Def']

        # 4. Clean text spacing issues & map short names before returning
        team_aggregates['Team'] = team_aggregates['Team'].astype(str).apply(lambda x: x.replace('\u00a0', ' ').strip())
        team_aggregates['short_name'] = team_aggregates['Team'].map(fpl_team_map)
        team_aggregates["Played"] = team_aggregates["Wins"] + team_aggregates["Draws"] + team_aggregates["Losses"]
        team_aggregates["xgA/90"] = team_aggregates["xG_Conceded"]/ team_aggregates["Played"]
        team_aggregates["xg/90"] = team_aggregates["xG_Created"]/ team_aggregates["Played"]
        team_aggregates.drop(columns=["Team_ID", "Team"])       
    return team_aggregates
"""


import json
import re

def fetch_understat():
    # 1. Targets the specific historical 2026 dataset endpoint
    url = "https://understat.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    # 2. Flexible regular expression matching any variable spacing or quotes variations
    pattern = r"teamsData\s*=\s*JSON\.parse\(['\"]([^'\"]+)['\"]\)"
    match = re.search(pattern, response.text)

    if match:
        # Pull the matched capturing group out safely
        json_raw_string = match.group(1)
        # Handle the unicode character escape layer back to standard dictionary variables
        decoded_json = json_raw_string.encode("utf8").decode("unicode_escape")
        leagues_data = json.loads(decoded_json)
    else:
        # FIX: Replaced st.error with a clean, standalone Python print statement
        print("Error: Understat data parsing failed. Bypassing execution hook safely.")
        return pd.DataFrame()

    # --- YOUR EXACT LOOP AND ANALYSIS RUNS UNTOUCHED BELOW ---
    all_matches = []
    for team_id, team_info in leagues_data.items():
        team_name = team_info["title"]
        understat_id = team_info["id"]

        for match in team_info["history"]:
            ppda_dict = match.get("ppda", {})
            ppda_allowed_dict = match.get("ppda_allowed", {})

            all_matches.append(
                {
                    "Team_ID": understat_id,
                    "Team": team_name,
                    "Goals_Scored": int(match.get("scored", 0)),
                    "Goals_Conceded": int(match.get("missed", 0)),
                    "Points": int(match.get("pts", 0)),
                    "Wins": int(match.get("wins", 0)),
                    "Draws": int(match.get("draws", 0)),
                    "Losses": int(match.get("loses", 0)),
                    "xG_Created": float(match.get("xG", 0)),
                    "xG_Conceded": float(match.get("xGA", 0)),
                    "npxG_Created": float(match.get("npxG", 0)),
                    "npxG_Conceded": float(match.get("npxGA", 0)),
                    "npxG_Difference": float(match.get("npxGD", 0)),
                    "Expected_Points": float(match.get("xpts", 0)),
                    "Deep_Passes_Completed": int(match.get("deep", 0)),
                    "Deep_Passes_Allowed": int(match.get("deep_allowed", 0)),
                    "PPDA_Attacking_Passes": int(ppda_dict.get("att", 0)),
                    "PPDA_Defensive_Actions": int(ppda_dict.get("def", 0)),
                    "PPDA_Allowed_Att": int(ppda_allowed_dict.get("att", 0)),
                    "PPDA_Allowed_Def": int(ppda_allowed_dict.get("def", 0)),
                }
            )

    df_matches = pd.DataFrame(all_matches)

    team_aggregates = (
        df_matches.groupby(["Team_ID", "Team"])
        .agg(
            {
                "Goals_Scored": "sum",
                "Goals_Conceded": "sum",
                "Points": "sum",
                "Wins": "sum",
                "Draws": "sum",
                "Losses": "sum",
                "xG_Created": "sum",
                "xG_Conceded": "sum",
                "npxG_Created": "sum",
                "npxG_Conceded": "sum",
                "npxG_Difference": "sum",
                "Expected_Points": "sum",
                "Deep_Passes_Completed": "sum",
                "Deep_Passes_Allowed": "sum",
                "PPDA_Attacking_Passes": "sum",
                "PPDA_Defensive_Actions": "sum",
                "PPDA_Allowed_Att": "sum",
                "PPDA_Allowed_Def": "sum",
            }
        )
        .reset_index()
    )

    team_aggregates["PPDA_Coeff"] = (
        team_aggregates["PPDA_Attacking_Passes"]
        / team_aggregates["PPDA_Defensive_Actions"]
    )
    team_aggregates["PPDA_Allowed_Coeff"] = (
        team_aggregates["PPDA_Allowed_Att"] / team_aggregates["PPDA_Allowed_Def"]
    )

    team_aggregates["Team"] = (
        team_aggregates["Team"]
        .astype(str)
        .apply(lambda x: x.replace("\u00a0", " ").strip())
    )
    team_aggregates["short_name"] = team_aggregates["Team"].map(fpl_team_map)
    team_aggregates["Played"] = (
        team_aggregates["Wins"]
        + team_aggregates["Draws"]
        + team_aggregates["Losses"]
    )
    team_aggregates["xgA/90"] = (
        team_aggregates["xG_Conceded"] / team_aggregates["Played"]
    )
    team_aggregates["xg/90"] = (
        team_aggregates["xG_Created"] / team_aggregates["Played"]
    )

    team_aggregates = team_aggregates.drop(columns=["Team_ID", "Team"])
    return team_aggregates


# function to fetch team data from FPL website
def fetch_team_data():
    understat_team_data = fetch_understat()
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    res = requests.get(url).json()
    df = pd.DataFrame(res['teams'])
    df.columns

    team_cols = [
        'id',
        'short_name',
        'position'
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

    # merge with understat data based on short name
    merged_team_df = pd.merge(team_df, understat_team_data, on="short_name", how= "inner")

    return merged_team_df


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
    
    # bring in the next 5 fixtures FDR Rating.
    player_df = player_df.merge(
        team_df[["short_name", "F1", "F2", "F3", "F4", "F5", "fdr_sum_next_5"]],
        left_on = "team",
        right_on = "short_name",
        how="left"
        ).drop(columns=["short_name"])

    # setting my team
    url = f"https://fantasy.premierleague.com/api/entry/{MANAGER_ID}/event/{GAMEWEEK}/picks/"
    response = requests.get(url).json()
    # Returns player element IDs, position order, and multipliers (1 for starter, 2 for captain)
    my_player_ids = [pick['element'] for pick in response['picks']]

    player_df["goal_involvements"] = player_df["goals_scored"] + player_df["assists"]
    player_df["in_my_team"] = False
    # Flag squad membership
    player_df["in_my_team"] = player_df["id"].isin(my_player_ids)

    outfield_df = player_df[player_df['element_type'] != 'GKP']

    # 2. Calculate the global league averages for Player Metrics (Season Totals)
    league_avg_xg = outfield_df['expected_goals'].mean()
    league_avg_xa = outfield_df['expected_assists'].mean()
    league_avg_threat = outfield_df['threat'].mean()
    league_avg_creativity = outfield_df['creativity'].mean()

    player_df['xgM'] = player_df['expected_goals']/league_avg_xg
    player_df['xaM'] = player_df['expected_assists']/league_avg_xa
    player_df['threatM'] = player_df['threat']/league_avg_threat
    player_df['creativityM'] = player_df['creativity']/league_avg_creativity

    player_df['attacking_index'] = 0.35 * player_df['xgM'] + 0.25 * (player_df['xaM'] + player_df['threatM']) + 0.15 * player_df['creativityM']
    player_df.drop(columns=['xaM', 'xgM', 'threatM', 'creativityM'], inplace=True)

    avg_team_xg_conceded = team_df['xG_Conceded'].mean()
    avg_team_deep_passes = team_df['Deep_Passes_Allowed'].mean()
    team_df['xg_conceded_mult'] = team_df['xG_Conceded'] / avg_team_xg_conceded
    team_df['deep_pass_mult'] = team_df['Deep_Passes_Allowed'] / avg_team_deep_passes
    team_df['defensive_multiplier'] = (0.70 * team_df['xg_conceded_mult']) + (0.30 * team_df['deep_pass_mult'])
    team_df.drop(columns=['xg_conceded_mult', 'deep_pass_mult'], inplace=True)
    def_lookup = dict(zip(team_df['short_name'], team_df['defensive_multiplier']))

    # similar stuff for defenders
    league_avg_def_contrib = outfield_df['defensive_contribution'].mean()
    league_avg_influence = outfield_df['influence'].mean()
    player_df['def_contribM'] = player_df['defensive_contribution'] / league_avg_def_contrib
    player_df['influenceM'] = player_df['influence'] / league_avg_influence
    player_df['defensive_index'] = (0.50 * player_df['def_contribM']) + (0.50 * player_df['influenceM'])
    player_df['own_team_leakiness'] = player_df['team'].map(def_lookup).fillna(1.0)
    player_df['base_defensive_power'] = player_df['defensive_index'] / player_df['own_team_leakiness'].replace(0, 0.01)
    player_df.drop(columns=['def_contribM', 'influenceM'], inplace=True)  

    avg_team_xg_created = team_df['xG_Created'].mean()
    avg_team_deep_completed = team_df['Deep_Passes_Completed'].mean()
    team_df['xg_created_mult'] = team_df['xG_Created'] / avg_team_xg_created
    team_df['deep_comp_mult'] = team_df['Deep_Passes_Completed'] / avg_team_deep_completed
    team_df['offensive_multiplier'] = (0.70 * team_df['xg_created_mult']) + (0.30 * team_df['deep_comp_mult'])
    team_df.drop(columns=['xg_created_mult', 'deep_comp_mult'], inplace=True)
    attack_lookup = dict(zip(team_df['short_name'], team_df['offensive_multiplier']))

    if 'F1' in player_df.columns:
        player_df["opp1"] = player_df["F1"].str.extract(r"^([A-Z]+)")
        player_df["opp2"] = player_df["F2"].str.extract(r"^([A-Z]+)")
        player_df["opp3"] = player_df["F3"].str.extract(r"^([A-Z]+)")
        player_df["opp4"] = player_df["F4"].str.extract(r"^([A-Z]+)")
        player_df["opp5"] = player_df["F5"].str.extract(r"^([A-Z]+)")

        player_df.drop(columns=["F2", "F3", "F4", "F5"], inplace=True)
    else:
        print("Warning: F1-F5 columns not found in player_df. Assuming opponent columns (opp1-opp5) were already created or will be handled elsewhere.")

    opp_cols = ['opp1', 'opp2', 'opp3', 'opp4', 'opp5']

    # Loop through each of the 5 upcoming games
    for i, col in enumerate(opp_cols, 1):
        if col in player_df.columns:
            # 1. Map the opponent's short-code to their defensive multiplier
            # fillna(1.0) keeps it at a neutral league average if a team code doesn't match
            opp_multiplier = player_df[col].map(def_lookup).fillna(1.0)
            
            # 2. Multiply the player's intrinsic index by the opponent's leakiness
            player_df[f'opp_{i}_att_score'] = player_df['attacking_index'] * opp_multiplier

            opp_att_multiplier = player_df[col].map(attack_lookup).fillna(1.0)
            player_df[f'opp_{i}_def_score'] = player_df['base_defensive_power'] / opp_att_multiplier.replace(0, 0.01)


    score_cols = [f'opp_{i}_att_score' for i in range(1, 6)]
    player_df['5gw_attack_score'] = player_df[score_cols].sum(axis=1)
    def_score_cols = [f'opp_{i}_def_score' for i in range(1, 6)]
    player_df['5gw_defense_score'] = player_df[def_score_cols].sum(axis=1)

    return player_df, team_df

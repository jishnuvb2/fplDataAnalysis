# this file is used to import the player data and team data
from config import MANAGER_ID
import pandas as pd
import requests

def get_latest_completed_gameweek():
    # 1. Hit the official base FPL API endpoint
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # 2. Filter for all gameweeks that have officially finished
        completed_gameweeks = [
            event['id'] for event in data['events'] if event['finished'] == True
        ]
        
        # 3. Return the maximum ID if any are found, otherwise return 0 (e.g., before GW1)
        return max(completed_gameweeks) if completed_gameweeks else 0
    else:
        raise Exception(f"Failed to fetch data from FPL API. Status code: {response.status_code}")

GAMEWEEK = get_latest_completed_gameweek()


# function to fetch team data from FPL website
def fetch_team_data():
    # FIX: Points to raw data instead of premierleague.com news layout
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    res = requests.get(url).json()
    df = pd.DataFrame(res['teams'])
    team_cols = [
        'id',
        'short_name',
        'position'
    ]
    team_df = df[team_cols] 

    # FIX: Points to raw data instead of premierleague.com news layout
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
    
    # FIX: Instantiates player_df using the full roster data object array
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

    player_df = player_df[player_df['minutes'] >= (player_df['minutes'].max()/4)]

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
    player_df["xGiPerformance"] = player_df['goal_involvements'] - player_df['expected_goal_involvements']
    return player_df, team_df


player_df, team_df = clean_data()

player_df.to_csv("pure_fpl_players.csv", index=False)
team_df.to_csv("pure_fpl_teams.csv", index=False)

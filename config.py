MANAGER_ID = 3411214  # Replace with your team ID
GAMEWEEK = 5

# defining what metrics mean
metrics_definition = {
    'Overall' : ["selected_by_percent", "points_per_game", "goal_involvements",
                "expected_goal_involvements", "clean_sheets", "expected_goals_conceded", "defensive_contribution",
                "bps", "now_cost"],
    'Attack' : ["selected_by_percent", "points_per_game", "goal_involvements",
                "expected_goal_involvements","now_cost", "influence", "threat", "creativity"],
    'Defence' : ["selected_by_percent", "points_per_game",
                "expected_goal_involvements", "clean_sheets", "expected_goals_conceded", "defensive_contribution",
                "bps", "now_cost", "fdr_sum_next_5"],
    'Captaincy' : ["selected_by_percent", "points_per_game", "goal_involvements",
                "expected_goal_involvements","now_cost", "influence", "threat", "creativity",
                "xga_opp1", "match_1_eGI"]
}

fpl_team_map = {
    'Arsenal': 'ARS',
    'Aston Villa': 'AVL',
    'Bournemouth': 'BOU',
    'Brentford': 'BRE',
    'Brighton': 'BHA',
    'Chelsea': 'CHE',
    'Coventry': 'COV',
    'Crystal Palace': 'CRY',
    'Everton': 'EVE',
    'Fulham': 'FUL',
    'Hull': 'HUL',
    'Ipswich': 'IPS',
    'Leeds': 'LEE',
    'Liverpool': 'LIV',
    'Manchester City': 'MCI',
    'Manchester United': 'MUN',
    'Newcastle United': 'NEW',
    'Nottingham Forest': 'NFO',
    'Sunderland': 'SUN',
    'Tottenham': 'TOT'
}

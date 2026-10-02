MANAGER_ID = 3411214  # Replace with your team ID

# defining what metrics mean
metrics_definition = {
    'Overall' : ["selected_by_percent", "points_per_game", "goal_involvements",
                "expected_goal_involvements", "5gw_attack_score", "5gw_defense_score",
                "bps", "now_cost"],
    
    'Attack' : ["selected_by_percent", "points_per_game", "goal_involvements",
                "expected_goal_involvements","now_cost", "5gw_attack_score", "threat", "creativity",
                ],
    
    'Defence' : ["selected_by_percent", "points_per_game",
                "expected_goal_involvements", "clean_sheets", "5gw_defense_score", "defensive_contribution",
                "bps", "now_cost", "5gw_attack_score", "base_defensive_power"],
    
    'Captaincy' : ["form", "expected_goal_involvements", "opp_1_att_score", "threat", "creativity", "bps"]
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




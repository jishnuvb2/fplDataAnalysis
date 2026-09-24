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
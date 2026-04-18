from nba_api.stats.endpoints import teamdashlineups
from nba_api.stats.static import teams
import pandas as pd
import time

# 1. Setup team mapping
nba_teams = teams.get_teams()
team_dict = {team['full_name']: team['id'] for team in nba_teams}


# 2. Updated Function for the 2025-26 Season
def get_lineups(team_id_i):
    # Note: season is now 2025-26
    lineup = teamdashlineups.TeamDashLineups(
        group_quantity=5,
        league_id_nullable="00",
        measure_type_detailed_defense="Base",
        per_mode_detailed="Totals",
        season="2025-26",
        season_type_all_star="Regular Season",
        team_id=team_id_i
    )

    # df[1] typically contains the Lineups summaries
    df = lineup.get_data_frames()
    return df[1]


# 3. Loop through teams and collect data
all_teams_list = []

for team_name, team_id in team_dict.items():
    print(f"Fetching data for: {team_name}...")
    try:
        team_lineup = get_lineups(team_id)
        team_lineup['team'] = team_name
        team_lineup['team_id'] = team_id
        all_teams_list.append(team_lineup)

        # Adding a small sleep to avoid hitting API rate limits
        time.sleep(0.6)
    except Exception as e:
        print(f"Could not retrieve data for {team_name}: {e}")

# 4. Concatenate all dataframes into one
# pd.append is deprecated; pd.concat is the modern, faster way.
league_lineup = pd.concat(all_teams_list, ignore_index=True)

# 5. Final processing
league_lineup['players_list'] = league_lineup['GROUP_NAME'].str.split(' - ')
league_lineup = league_lineup.sort_values(by='team')

# Save to the new CSV name
league_lineup.to_csv('nba2026.csv', index=False)
print("File 'nba2026.csv' has been created successfully.")
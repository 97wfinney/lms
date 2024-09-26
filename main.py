import json
import requests

BASE_URL = "https://fantasy.premierleague.com/api/"

# Fetch data from the FPL API
def fetch_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch data from {url}.")
        return None
    return response.json()

# Fetch bootstrap data (teams, players, events)
def fetch_bootstrap_data():
    url = BASE_URL + "bootstrap-static/"
    return fetch_data(url)

# Fetch fixtures for the next gameweek
def fetch_fixtures(next_gw):
    url = f"{BASE_URL}fixtures/"
    fixtures = fetch_data(url)
    upcoming_fixtures = [f for f in fixtures if f['event'] == next_gw]
    return upcoming_fixtures

# Determine the current gameweek
def get_current_gameweek(data):
    for event in data['events']:
        if event['is_current']:
            return event['id']
    return None

# Load previous selections from the text file
def load_previous_selections(filepath):
    with open(filepath, 'r') as f:
        return set(line.strip().lower() for line in f)

# Append the selected team to the text file
def append_to_txt_file(filepath, team_name):
    with open(filepath, 'a') as f:
        f.write(f"{team_name.lower()}\n")

# Calculate the team strength score
def calculate_team_strength(team_data, opponent_team_data, is_home):
    attack_strength = float(team_data.get('strength_attack_home', 0) if is_home else team_data.get('strength_attack_away', 0))
    defence_strength = float(team_data.get('strength_defence_home', 0) if is_home else team_data.get('strength_defence_away', 0))
    overall_strength = float(team_data.get('strength_overall_home', 0) if is_home else team_data.get('strength_overall_away', 0))

    opponent_defense_strength = float(opponent_team_data.get('strength_defence_home', 0) if is_home else opponent_team_data.get('strength_defence_away', 0))

    # Simple weighted score calculation
    difficulty_adjustment = attack_strength / opponent_defense_strength if opponent_defense_strength > 0 else 1
    score = (0.4 * attack_strength + 0.4 * defence_strength + 0.2 * overall_strength) * difficulty_adjustment
    
    return score

# Find the strongest available team
def find_strongest_team(teams_data, fixtures, previous_selections):
    team_scores = []

    for fixture in fixtures:
        home_team = next(team for team in teams_data if team['id'] == fixture['team_h'])
        away_team = next(team for team in teams_data if team['id'] == fixture['team_a'])
        
        home_strength = calculate_team_strength(home_team, away_team, is_home=True)
        away_strength = calculate_team_strength(away_team, home_team, is_home=False)
        
        team_scores.append((home_team['name'], home_team['short_name'], home_strength))
        team_scores.append((away_team['name'], away_team['short_name'], away_strength))
    
    # Sort the teams from strongest to weakest
    team_scores.sort(key=lambda x: x[2], reverse=True)

    # Print the sorted list of all teams
    print("Teams from strongest to weakest for the next gameweek:")
    for team in team_scores:
        chosen_status = " (Previously chosen)" if team[0].lower() in previous_selections else ""
        print(f"{team[0]} ({team[1]}) - Strength: {team[2]:.2f}{chosen_status}")

    # Filter out previously selected teams
    available_teams = [team for team in team_scores if team[0].lower() not in previous_selections]

    # Return the strongest available team
    return available_teams[0] if available_teams else None

# Save data to JSON file
def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    # Fetch the bootstrap data
    data = fetch_bootstrap_data()
    if not data:
        print("Error fetching bootstrap data.")
        return
    
    # Save the fetched data to a JSON file
    save_to_json(data, "players_data_gw.json")
    print("FPL data saved to players_data_gw.json")
    
    # Determine the current gameweek
    current_gw = get_current_gameweek(data)
    if not current_gw:
        print("Current gameweek could not be determined.")
        return
    
    # Fetch the fixtures for the next gameweek (current_gw + 1)
    next_gw = current_gw + 1
    fixtures = fetch_fixtures(next_gw)
    
    # Load previous selections from text file
    txt_filepath = "lms.txt"  # Path to your previous selections file
    previous_selections = load_previous_selections(txt_filepath)
    
    # Print previous selections
    print("\nPrevious selections:")
    for selection in previous_selections:
        print(selection.title())
    
    # Find the strongest available team for the next gameweek
    strongest_team = find_strongest_team(data['teams'], fixtures, previous_selections)
    
    if strongest_team:
        print(f"\nSuggested team for Gameweek {next_gw}: {strongest_team[0]} ({strongest_team[1]}) with strength {strongest_team[2]:.2f}")
        
        # Append the selected team to the lms.txt file
        append_to_txt_file(txt_filepath, strongest_team[0])
        print(f"\n{strongest_team[0]} has been added to the previous selections.")
    else:
        print("No available teams left to choose.")

if __name__ == "__main__":
    main()
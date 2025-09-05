#gets results from EFL 24-25 season ONLY
import requests

API_TOKEN = '581c6d4cd5014a5d906c1ff9538f9448'
headers = {'X-Auth-Token': API_TOKEN}

url = 'https://api.football-data.org/v4/competitions/ELC/matches'  # ELC = EFL Championship

params = {
    'season': 2024,                 # 2024–25 season
    'dateFrom': '2024-05-28',       # Start date
    'dateTo': '2025-06-28'          # End date
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    matches = response.json().get('matches', [])
    
    if matches:
        for match in matches:
            utc_date = match['utcDate'][:10]
            home = match['homeTeam']['name']
            away = match['awayTeam']['name']
            status = match['status']
            score = match['score']['fullTime']
            print(f"{utc_date}: {home} {score['home']} - {score['away']} {away} ({status})")
    else:
        print("No matches found in that range.")
else:
    print(f"Failed to retrieve matches: {response.status_code}")
    print("Response Content:", response.text)
    
    
    """
    #Returns last EFL season's home records for each team
def get_home_EFL_record(team_name, season_year):
    url = f'https://api.football-data.org/v4/competitions/ELC/standings?season={season_year}'
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve data: {response.status_code}")
        return None

    data = response.json()
    standings = data.get('standings', [])

    # Extract HOME table
    home_table = next((s['table'] for s in standings if s['type'] == 'HOME'), [])
    
    for team in home_table:
        name = team['team']['name']
        if name.lower() == team_name.lower():
            won = team.get('won', 0)
            draw = team.get('draw', 0)
            lost = team.get('lost', 0)
            total = 19
            return [won/total, draw/total, lost/total]

    print(f"Team '{team_name}' not found in the EFL standings.")
    return None

#print(get_home_EFL_record("Burnley FC", 2024))

#Returns last EFL season's away records for each team
def get_away_EFL_record(team_name, season_year):
    url = f'https://api.football-data.org/v4/competitions/ELC/standings?season={season_year}'
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve data: {response.status_code}")
        return None

    data = response.json()
    standings = data.get('standings', [])

    # Extract AWAY table
    away_table = next((s['table'] for s in standings if s['type'] == 'AWAY'), [])
    
    for team in away_table:
        name = team['team']['name']
        if name.lower() == team_name.lower():
            won = team.get('won', 0)
            draw = team.get('draw', 0)
            lost = team.get('lost', 0)
            total = 19
            return [won/total, draw/total, lost/total]

    print(f"Team '{team_name}' not found in the EFL standings.")
    return None

#print(get_away_EFL_record("Leeds United FC", 2024))
    """
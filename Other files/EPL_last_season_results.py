#gets results from EPL 24-25 season ONLY
import requests

API_TOKEN = '581c6d4cd5014a5d906c1ff9538f9448'
headers = {'X-Auth-Token': API_TOKEN}

url = 'https://api.football-data.org/v4/competitions/PL/matches'
params = {
    'season': 2024,               # 2023–24 season
    'dateFrom': '2024-05-28',     # Match day (last matchweek of 23–24 season)
    'dateTo': '2025-06-28'        
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
        print("No matches found on that date.")
else:
    print(f"Failed to retrieve matches: {response.status_code}")
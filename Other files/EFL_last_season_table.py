#get efl championship table standings
import requests

API_TOKEN = '581c6d4cd5014a5d906c1ff9538f9448'
headers = {'X-Auth-Token': API_TOKEN}

season_year = 2024  # 2024–25 season
url = f'https://api.football-data.org/v4/competitions/ELC/standings?season={season_year}'

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    standings = data.get('standings', [])

    if standings:
        # Extract TOTAL, HOME, AWAY tables
        total_table = next((s['table'] for s in standings if s['type'] == 'TOTAL'), [])
        home_table = next((s['table'] for s in standings if s['type'] == 'HOME'), [])
        away_table = next((s['table'] for s in standings if s['type'] == 'AWAY'), [])

        # Create quick lookup dicts by team ID for home and away
        home_stats = {team['team']['id']: team for team in home_table}
        away_stats = {team['team']['id']: team for team in away_table}

        # Print header with home/away added
        header = (f"{'Pos':<4} {'Team':<30} {'P':<3} {'W':<3} {'D':<3} {'L':<3} "
                f"{'GF':<4} {'GA':<4} {'GD':<4} {'Pts':<4} {'Form':<15} "
                f"{'Home W-D-L':<10} {'Away W-D-L':<10}")
        print(header)
        print("-" * len(header))

        # Print overall + home/away for each team
        for team in total_table:
            tid = team['team']['id']
            pos = team['position']
            name = team['team']['name']
            played = team['playedGames']
            won = team['won']
            draw = team['draw']
            lost = team['lost']
            gf = team['goalsFor']
            ga = team['goalsAgainst']
            gd = team['goalDifference']
            pts = team['points']
            form = team.get('form', '')

            # Get home and away W-D-L
            home = home_stats.get(tid, {})
            away = away_stats.get(tid, {})
            home_record = f"{home.get('won', 0)}-{home.get('draw', 0)}-{home.get('lost', 0)}"
            away_record = f"{away.get('won', 0)}-{away.get('draw', 0)}-{away.get('lost', 0)}"

            print(f"{pos:<4} {name:<30} {played:<3} {won:<3} {draw:<3} {lost:<3} "
                f"{gf:<4} {ga:<4} {gd:<4} {pts:<4} {form:<15} "
                f"{home_record:<10} {away_record:<10}")

    else:
        print("No standings data available.")
else:
    print(f"Failed to retrieve data: {response.status_code}")
    print("Response Content:", response.text)
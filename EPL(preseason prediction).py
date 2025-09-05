from pprint import PrettyPrinter
printer = PrettyPrinter()

import random
import requests
API_TOKEN = ''
headers = {'X-Auth-Token': API_TOKEN}

This_season_EPL_teams = ["Liverpool FC" , "Arsenal FC" , 
    "Manchester City FC", "Chelsea FC", "Newcastle United FC", 
    "Manchester United FC", "Tottenham Hotspur FC", "Aston Villa FC",
    "Brighton & Hove Albion FC", "Nottingham Forest FC",
    "AFC Bournemouth", "Everton FC",  "Fulham FC", "West Ham United FC",
    "Crystal Palace FC", "Brentford FC", "Leeds United FC", 
    "Wolverhampton Wanderers FC", "Burnley FC", "Sunderland AFC"]

Last_season_EPL_teams = ["Liverpool FC" , "Arsenal FC" , 
    "Manchester City FC", "Chelsea FC", "Newcastle United FC", 
    "Manchester United FC", "Tottenham Hotspur FC", "Aston Villa FC",
    "Brighton & Hove Albion FC", "Nottingham Forest FC",
    "AFC Bournemouth", "Everton FC",  "Fulham FC", "West Ham United FC",
    "Crystal Palace FC", "Brentford FC",  "Wolverhampton Wanderers FC"]

Last_season_EFL_teams = ["Leeds United FC", "Burnley FC", 
                        "Sunderland AFC"]

#Predicted table in form {team: [pts, played, won, draw, lost]}
PREDICTED_TABLE = {'Liverpool FC': [0,0,0,0,0], 'Arsenal FC': [0,0,0,0,0], 
        'Manchester City FC': [0,0,0,0,0], 'Chelsea FC': [0,0,0,0,0], 
        'Newcastle United FC': [0,0,0,0,0], 'Manchester United FC': [0,0,0,0,0], 
        'Tottenham Hotspur FC': [0,0,0,0,0] , 'Aston Villa FC': [0,0,0,0,0], 
        'Brighton & Hove Albion FC': [0,0,0,0,0], 'Nottingham Forest FC': [0,0,0,0,0], 
        'AFC Bournemouth': [0,0,0,0,0], 'Everton FC': [0,0,0,0,0], 'Fulham FC': [0,0,0,0,0], 
        'West Ham United FC': [0,0,0,0,0], 'Crystal Palace FC': [0,0,0,0,0], 
        'Brentford FC': [0,0,0,0,0], 'Leeds United FC': [0,0,0,0,0], 
        'Wolverhampton Wanderers FC': [0,0,0,0,0], 'Burnley FC': [0,0,0,0,0] , 'Sunderland AFC': [0,0,0,0,0]}

#LIST OF ALL PREDICTED RESULTS in form {game: result}
PREDICTED_RESULTS = {}


######GET MATCH RESULT BASED ON PRESEASON ODDS#########
Betting_odds = {
    "Liverpool FC":"2/1", "Arsenal FC":"9/4", 
    "Manchester City FC":"3/1", "Chelsea FC":"8/1",
    "Newcastle United FC":"28/1", "Manchester United FC":"40/1",
    "Tottenham Hotspur FC":"50/1", "Aston Villa FC":"66/1",
    "Brighton & Hove Albion FC":"150/1", "Nottingham Forest FC":"200/1",
    "AFC Bournemouth":"350/1", "Everton FC":"500/1", 
    "Fulham FC":"750/1", "West Ham United FC":"500/1",
    "Crystal Palace FC":"750/1", "Brentford FC":"1000/1",
    "Leeds United FC":"1000/1", "Wolverhampton Wanderers FC":"1000/1",
    "Burnley FC":"1500/1", "Sunderland AFC":"2000/1"
}

#Gets probability of each team winning the league based on given odds
def get_odd_probs(betting_odds):        
    bet_prob = {}
    
    for team in betting_odds:
        numerator = int(betting_odds[team].split("/")[1])
        denominator = int(betting_odds[team].split("/")[0]) + numerator
        probability = numerator/denominator
        
        bet_prob[team] = probability
    return bet_prob

BET_PROB = get_odd_probs(Betting_odds)

#Gives each team a strength rating using probabilities to win the league
def strength_rating(BET_PROB):
    BET_PROB2 = {}
    strength_ratings = {}
    
    for team in BET_PROB:
        BET_PROB2[team]  = BET_PROB[team] ** 0.25     #power transformation to even teams out
    max_val = max(BET_PROB2.values())
    
    for team in BET_PROB2:
        BET_PROB2[team] = (BET_PROB2[team]/max_val)*100      #get strength rating    
    
    return BET_PROB2

STRENGTH_RATINGS = strength_rating(BET_PROB)

#printer.pprint(BET_PROB) 
#printer.pprint(STRENGTH_RATINGS) 

#Returns probabilities of how match can finish based on 2 teams
def match_result_prob(hteam_strength, ateam_strength):
    
    #Team A has a "strength_ratio"% chance of not losing
    strength_ratio = hteam_strength / (hteam_strength + ateam_strength)

    #Allocate probabilities of match outcome using simple heuristic 
    #draw_prob: depends on how close 2 teams are on strength (assumes 0.4 for max draw_prob)

    draw_prob = 0.4 - abs(strength_ratio - 0.5)
    hteam_win_prob = strength_ratio * (1-draw_prob)
    ateam_win_prob = (1-strength_ratio) * (1-draw_prob)

    return [hteam_win_prob, draw_prob, ateam_win_prob]

"""
match_prob = match_result_prob(STRENGTH_RATINGS["Liverpool FC"], 
                    STRENGTH_RATINGS["Arsenal FC"])
printer.pprint(match_prob)
"""

######GET HOME AND AWAY PROBABILITIES BASED ON RECORDS FROM LAST SEASON#########

#Returns last EPL season's home records for each team
def get_home_EPL_record(team_name, season_year):
    url = f'https://api.football-data.org/v4/competitions/PL/standings?season={season_year}'
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

    print(f"Team '{team_name}' not found in the Premier League standings.")
    return None

#print(get_home_EPL_record("Manchester United FC", 2024))

#puts all of last season's home records in a dictionary
def get_all_home_records():
    LAST_SEASON_HOME_RECORDS = {}       #in form: {team: [won, draw, lost]}

    for team in This_season_EPL_teams:
            LAST_SEASON_HOME_RECORDS[team] = get_home_EPL_record(team, 2024)
    return LAST_SEASON_HOME_RECORDS

#used get_all_home_records to fill this
LAST_SEASON_HOME_RECORDS = {'Liverpool FC': [0.7368421052631579, 0.21052631578947367, 0.05263157894736842], 
                            'Arsenal FC': [0.5789473684210527, 0.3157894736842105, 0.10526315789473684], 
                            'Manchester City FC': [0.6842105263157895, 0.15789473684210525, 0.15789473684210525], 
                            'Chelsea FC': [0.631578947368421, 0.2631578947368421, 0.10526315789473684], 
                            'Newcastle United FC': [0.631578947368421, 0.10526315789473684, 0.2631578947368421], 
                            'Manchester United FC': [0.3684210526315789, 0.15789473684210525, 0.47368421052631576], 
                            'Tottenham Hotspur FC': [0.3157894736842105, 0.15789473684210525, 0.5263157894736842], 
                            'Aston Villa FC': [0.5789473684210527, 0.3684210526315789, 0.05263157894736842], 
                            'Brighton & Hove Albion FC': [0.42105263157894735, 0.42105263157894735, 0.15789473684210525], 
                            'Nottingham Forest FC': [0.47368421052631576, 0.2631578947368421, 0.2631578947368421], 
                            'AFC Bournemouth': [0.42105263157894735, 0.21052631578947367, 0.3684210526315789],
                            'Everton FC': [0.2631578947368421, 0.47368421052631576, 0.2631578947368421], 
                            'Fulham FC': [0.3684210526315789, 0.2631578947368421, 0.3684210526315789], 
                            'West Ham United FC': [0.2631578947368421, 0.2631578947368421, 0.47368421052631576], 
                            'Crystal Palace FC': [0.3157894736842105, 0.3684210526315789, 0.3157894736842105],
                            'Brentford FC': [0.47368421052631576, 0.21052631578947367, 0.3157894736842105], 
                            'Wolverhampton Wanderers FC': [0.3157894736842105, 0.15789473684210525, 0.5263157894736842]}      
#print(LAST_SEASON_HOME_RECORDS)


#Returns last EPL season's away records for each team
def get_away_EPL_record(team_name, season_year):
    url = f'https://api.football-data.org/v4/competitions/PL/standings?season={season_year}'
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

    print(f"Team '{team_name}' not found in the Premier League standings.")
    return None

#print(get_away_EPL_record("Liverpool FC", 2024))

#puts all of last season's away records in a dictionary
def get_all_away_records():
    LAST_SEASON_AWAY_RECORDS = {}       #in form: {team: [won, draw, lost]}

    for team in Last_season_EPL_teams:
            LAST_SEASON_AWAY_RECORDS[team] = get_away_EPL_record(team, 2024)
    return LAST_SEASON_AWAY_RECORDS

#used get_all_away_records to fill this
LAST_SEASON_AWAY_RECORDS = {'Liverpool FC': [0.5789473684210527, 0.2631578947368421, 0.15789473684210525], 
                            'Arsenal FC': [0.47368421052631576, 0.42105263157894735, 0.10526315789473684], 
                            'Manchester City FC': [0.42105263157894735, 0.2631578947368421, 0.3157894736842105], 
                            'Chelsea FC': [0.42105263157894735, 0.21052631578947367, 0.3684210526315789], 
                            'Newcastle United FC': [0.42105263157894735, 0.21052631578947367, 0.3684210526315789], 
                            'Manchester United FC': [0.21052631578947367, 0.3157894736842105, 0.47368421052631576], 
                            'Tottenham Hotspur FC': [0.2631578947368421, 0.10526315789473684, 0.631578947368421], 
                            'Aston Villa FC': [0.42105263157894735, 0.10526315789473684, 0.47368421052631576], 
                            'Brighton & Hove Albion FC': [0.42105263157894735, 0.2631578947368421, 0.3157894736842105], 
                            'Nottingham Forest FC': [0.5263157894736842, 0.15789473684210525, 0.3157894736842105], 
                            'AFC Bournemouth': [0.3684210526315789, 0.3684210526315789, 0.2631578947368421],
                            'Everton FC': [0.3157894736842105, 0.3157894736842105, 0.3684210526315789], 
                            'Fulham FC': [0.42105263157894735, 0.21052631578947367, 0.3684210526315789], 
                            'West Ham United FC': [0.3157894736842105, 0.2631578947368421, 0.42105263157894735], 
                            'Crystal Palace FC': [0.3684210526315789, 0.3684210526315789, 0.2631578947368421], 
                            'Brentford FC': [0.3684210526315789, 0.21052631578947367, 0.42105263157894735], 
                            'Wolverhampton Wanderers FC': [0.3157894736842105, 0.15789473684210525, 0.5263157894736842]}
#print(LAST_SEASON_AWAY_RECORDS)


#CALCULATE FINAL PROBABILITIES FOR ONE MATCH
def final_match_prob(hteam, ateam):

    #extract probabilities from preseason odds/strength ratings
    hteam_win_prob1 = match_result_prob(STRENGTH_RATINGS[hteam], 
                    STRENGTH_RATINGS[ateam])[0]
    draw_prob1 = match_result_prob(STRENGTH_RATINGS[hteam], 
                    STRENGTH_RATINGS[ateam])[1]
    ateam_win_prob1 = match_result_prob(STRENGTH_RATINGS[hteam], 
                    STRENGTH_RATINGS[ateam])[2]
    
    #extract probabilities based on home and away records for each EPL team
    
    if hteam in Last_season_EPL_teams and ateam in Last_season_EPL_teams:
        
        hteam_win_prob2_1 = LAST_SEASON_HOME_RECORDS[hteam][0]
        hteam_draw_prob2_1 = LAST_SEASON_HOME_RECORDS[hteam][1]
        hteam_lost_prob2_1 = LAST_SEASON_HOME_RECORDS[hteam][2]
        
        ateam_win_prob2_1 = LAST_SEASON_AWAY_RECORDS[ateam][0]
        ateam_draw_prob2_1 = LAST_SEASON_AWAY_RECORDS[ateam][1]
        ateam_lost_prob2_1 = LAST_SEASON_AWAY_RECORDS[ateam][2]
        
        hteam_win_prob2 = (hteam_win_prob2_1 + ateam_lost_prob2_1)/2
        draw_prob2 = (hteam_draw_prob2_1 + ateam_draw_prob2_1)/2
        ateam_win_prob2 = (hteam_lost_prob2_1 + ateam_win_prob2_1)/2
    
    
    #Use results from 2 sources (or less) to determine final match probabilities
    
    if hteam in Last_season_EPL_teams and ateam in Last_season_EPL_teams:   #2 epl teams
        
        HTEAM_WIN_PROB = hteam_win_prob1 * 0.75 + hteam_win_prob2 * 0.25 
        DRAW_PROB = draw_prob1 * 0.75 + draw_prob2 * 0.25
        ATEAM_WIN_PROB = ateam_win_prob1 * 0.75 + ateam_win_prob2 * 0.25

        return [HTEAM_WIN_PROB, DRAW_PROB, ATEAM_WIN_PROB]
    
    else:       #(1 epl team and 1 efl team) or (2 efl teams)
        HTEAM_WIN_PROB = hteam_win_prob1 
        DRAW_PROB = draw_prob1 
        ATEAM_WIN_PROB = ateam_win_prob1
        
        return [HTEAM_WIN_PROB, DRAW_PROB, ATEAM_WIN_PROB]


#DECIDE RESULT OF MATCH BASED ON PROBABILITY
def simulate_result(hteam, ateam):
    probabilities = final_match_prob(hteam, ateam)  #get match probabilities

    outcomes = [hteam + ' wins', "Draw", ateam + " wins"]   #possible outcome
    result = random.choices(outcomes, weights=probabilities, k=1)[0]    #capture result
    
    return result

#print(simulate_result("Liverpool FC", "Arsenal FC")

#UPDATES TABLE BASED ON MATCH RESULTS
def update_table(hteam, ateam, result):
    
    #update predicted league table after each result
    if result == hteam + ' wins':
        PREDICTED_TABLE[hteam][0] += 3      #3 points for winning team
        PREDICTED_TABLE[hteam][1] += 1      #1 more game played
        PREDICTED_TABLE[hteam][2] += 1     #1 more win
        
        PREDICTED_TABLE[ateam][1] += 1
        PREDICTED_TABLE[ateam][4] += 1      #1 more loss
    
    elif result == "Draw":
        PREDICTED_TABLE[hteam][0] += 1      #1 point for draw
        PREDICTED_TABLE[ateam][0] += 1
        PREDICTED_TABLE[hteam][1] += 1      #1 moore game played
        PREDICTED_TABLE[ateam][1] += 1
        PREDICTED_TABLE[hteam][3] += 1      #1 more draw
        PREDICTED_TABLE[ateam][3] += 1
    
    else:
        PREDICTED_TABLE[ateam][0] += 3      #3 points for winning team
        PREDICTED_TABLE[ateam][1] += 1      #1 more game played
        PREDICTED_TABLE[ateam][2] += 1     #1 more win
        
        PREDICTED_TABLE[hteam][1] += 1
        PREDICTED_TABLE[hteam][4] += 1      #1 more loss

#SIMULATES ENTIRE LEAGUE SEASON
def simulate_league():
    
    #simulate all matches
    for i in range(len(This_season_EPL_teams)):
        for j in range(i+1, len(This_season_EPL_teams)):
            team1 = This_season_EPL_teams[i]
            team2 = This_season_EPL_teams[j]
            
            #simulate both matches
            game1_result = simulate_result(team1, team2)
            PREDICTED_RESULTS[team1 + ' vs ' + team2] = game1_result     #add result to results list
            update_table(team1, team2, game1_result)        #update table
            
            game2_result = simulate_result(team2, team1)
            PREDICTED_RESULTS[team2 + ' vs ' + team1] = game2_result     #add result to results list
            update_table(team2, team1, game2_result)        #update table

simulate_league()

#sort final league table
sorted_table = sorted(PREDICTED_TABLE.items(), key=lambda x: (-x[1][0], x[0]))

#Displays sorted table in terminal
"""
for i, (team, stats) in enumerate(sorted_table, 1):
    print(f"{i}. {team}: {stats[0]} pts, {stats[2]}W {stats[3]}D {stats[4]}L")
"""

#printer.pprint(PREDICTED_RESULTS)      #prints all results


#####DISPLAY LEAGUE TABLE IN NEW WINDOW#####
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

#TEAM LOGOS DICTIONARY
TEAM_LOGOS = {'Liverpool FC': 'logos/Liverpool_FC logo.png', 'Arsenal FC': 'logos/Arsenal.png', 
        'Manchester City FC': 'logos/Man City.png', 'Chelsea FC': 'logos/Chelsea.png', 
        'Newcastle United FC': 'logos/Newcastle.png', 'Manchester United FC': 'logos/Man United.png', 
        'Tottenham Hotspur FC': 'logos/Tottenham.png' , 'Aston Villa FC': 'logos/Aston Villa.png', 
        'Brighton & Hove Albion FC': 'logos/Brighton.png', 'Nottingham Forest FC': 'logos/NForest.png', 
        'AFC Bournemouth': 'logos/Bournemouth.jpeg', 'Everton FC': 'logos/Everton.png', 'Fulham FC': 'logos/Fulham.png', 
        'West Ham United FC': 'logos/West Ham.png', 'Crystal Palace FC': 'logos/Palace.png', 
        'Brentford FC': 'logos/Brentford.png', 'Leeds United FC': 'logos/Leeds.png', 
        'Wolverhampton Wanderers FC': 'logos/Wolves.png', 'Burnley FC': 'logos/Burnley.png' , 'Sunderland AFC': 'logos/Sunderland.png'}


def show_league_table(table):
    root = tk.Tk()
    root.title("2025-2026 Premier League Predicted Table")
    root.geometry("700x900")

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    headers = ["Pos", "Logo", "Team", "Pts", "P", "W", "D", "L"]
    for col, h in enumerate(headers):
        tk.Label(scroll_frame, text=h, font=("Arial", 12, "bold"), borderwidth=1, relief="solid",
            bg="#d1d1d1", padx=8,pady=10).grid(row=0, column=col, padx=1, pady=1, sticky="nsew")

    logo_images = []  # To keep references and prevent garbage collection

    for i, (team, stats) in enumerate(table, 1):
        bg_color = "#f9f9f9" if i % 2 == 0 else "white"

        tk.Label(scroll_frame, text=str(i), borderwidth=1, relief="solid",
            bg=bg_color, padx=6, pady=10 ).grid(row=i, column=0, sticky="nsew")

        # Logo column
        logo_path = TEAM_LOGOS.get(team)
        if logo_path:
            img = Image.open(logo_path).resize((40, 45))
            img_tk = ImageTk.PhotoImage(img)
            logo_images.append(img_tk)
            tk.Label( scroll_frame, image=img_tk, borderwidth=1, relief="solid", 
                        bg=bg_color).grid(row=i, column=1, padx=1, pady=1)
        else:
            tk.Label( scroll_frame, text="N/A", borderwidth=1, relief="solid",
                bg=bg_color ).grid(row=i, column=1, padx=1, pady=1)

        tk.Label(scroll_frame, text=team, borderwidth=1, relief="solid",
            bg=bg_color, padx=6, pady=10 ).grid(row=i, column=2, sticky="nsew")

        for j, value in enumerate(stats[:5], start=3):  # Pts, P, W, D, L
            tk.Label(scroll_frame, text=str(value), borderwidth=1,relief="solid",
                bg=bg_color, padx=6, pady=10).grid(row=i, column=j, sticky="nsew")
    root.mainloop()

show_league_table(sorted_table)
            
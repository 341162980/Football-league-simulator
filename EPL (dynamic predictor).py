#get this season's team stats 
import requests
import random
from pprint import PrettyPrinter
printer = PrettyPrinter()

API_TOKEN = ''
headers = {'X-Auth-Token': API_TOKEN}

EPL_TEAMS = ["Liverpool FC" , "Arsenal FC" , 
    "Manchester City FC", "Chelsea FC", "Newcastle United FC", 
    "Manchester United FC", "Tottenham Hotspur FC", "Aston Villa FC",
    "Brighton & Hove Albion FC", "Nottingham Forest FC",
    "AFC Bournemouth", "Everton FC",  "Fulham FC", "West Ham United FC",
    "Crystal Palace FC", "Brentford FC", "Leeds United FC", 
    "Wolverhampton Wanderers FC", "Burnley FC", "Sunderland AFC"]

#LIST OF ALL PREDICTED RESULTS in form {game: result}
PREDICTED_RESULTS = {}

##### RETURNS CURRENT SEASON TABLE (position, pts, played ,record, form)#####
def get_team_info():
    season_year = 2025      #select season
    url = f'https://api.football-data.org/v4/competitions/PL/standings?season={season_year}'
    response = requests.get(url, headers=headers)

    data = response.json()
    standings = data.get('standings', [])

    total_table = next((s['table'] for s in standings if s['type'] == 'TOTAL'), [])
    summary_dict = {}

    for team in total_table:
        team_name = team['team']['name']
        pts = team['points']
        pos = team['position']
        played = team['playedGames']
        won = team['won']
        draw = team['draw']
        lost = team['lost']
        form = team.get('form', 'N/A')
        
        summary_dict[team_name] = [pos,pts, played, [won, draw, lost], form]

    return summary_dict

TEAM_STATS = get_team_info()
#printer.pprint(TEAM_STATS)

##### RETURNS ALL GAMES (BOTH COMPLETE AND INCOMPLETE )#####
def get_all_games():
    url = 'https://api.football-data.org/v4/competitions/PL/matches'
    params = {'season': 2025,  }
    response = requests.get(url, headers=headers, params=params)

    matches = response.json().get('matches', [])
        
    if matches:
        for match in matches:
            home = match['homeTeam']['name']
            away = match['awayTeam']['name']
            status = match['status']
            score = match['score']['fullTime']
            print(f"{home} {score['home']} - {score['away']} {away} ({status})")
    else:
        print("No matches found on that date.")

#get_all_games()

##### GET MATCH RESULT PROBABILITIES BASED ON PRESEASON ODDS #####
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


#####GET MATCH PROBABILITIES BASED ON CURRENT LEAGUE RECORD#####
def match_result_prob1(hteam, ateam):
    
    #no games played yet
    if TEAM_STATS[hteam][2] ==0 or TEAM_STATS[ateam][2] ==0:
        return [0,0,0]
    
    h_wins, h_draws, h_losses = TEAM_STATS[hteam][3]
    a_wins, a_draws, a_losses = TEAM_STATS[ateam][3]

    h_win_prob = h_wins / TEAM_STATS[hteam][2]
    h_draw_prob = h_draws / TEAM_STATS[hteam][2]
    h_loss_prob = h_losses / TEAM_STATS[hteam][2]

    a_win_prob = a_wins / TEAM_STATS[ateam][2]
    a_draw_prob = a_draws / TEAM_STATS[ateam][2]
    a_loss_prob = a_losses / TEAM_STATS[ateam][2]

    #final probabilities
    hteam_win = (h_win_prob + a_loss_prob) / 2
    draw = (h_draw_prob + a_draw_prob) / 2
    ateam_win = (a_win_prob + h_loss_prob) / 2

    return [hteam_win, draw, ateam_win]

#print(match_result_prob1('Liverpool FC', 'Arsenal FC'))


######GET MATCH PROBABILITIES RECENT FORM#####
def read_form(team):        #turn recent form string into probability
    form = TEAM_STATS[team][4]
    if len(form)<1:     #no games yet
        return [0,0,0]
    
    form = form.replace(',', '')       #remove commas
    #print(form)
    won = 0
    draw = 0
    lost = 0
    for i in range(0, len(form)):
        if form[i]=='W':
            won +=1
        elif form[i]=='D':
            draw +=1
        else:
            lost+=1
    return [won/len(form), draw/len(form), lost/len(form)]

#print(read_form('Liverpool FC'))

def match_result_prob2(hteam, ateam):      #get match prob from recent form
    hteam_form = read_form(hteam)
    ateam_form = read_form(ateam)

    hteam_win_prob = (hteam_form[0] + ateam_form[2])/2
    draw_prob = (hteam_form[1] + ateam_form[1])/2
    ateam_win_prob = (hteam_form[2] + ateam_form[0])/2
    
    return [hteam_win_prob, draw_prob, ateam_win_prob]

#print(match_result_prob2('Liverpool FC', 'Arsenal FC'))


######ADD WEIGHTING FROM DIFFERENT FACTORS######
def factor_weights():
    games_played = 0
    for team in TEAM_STATS:
        games_played += TEAM_STATS[team][2]
    season_progress = (games_played/2) / 380     #find how much season has progressed
    preseason_weight = (1 - season_progress)**2     #preseason weight decrease as season progresses
    record_weight = season_progress * 0.8       #record gets 80% remaining weight
    form_weight = season_progress * 0.2    #form gets 20% remaining weight

    weights = [preseason_weight, record_weight, form_weight]
    return weights

#print(factor_weights())


##### PREDICTING (GIVEN BOTH PRESEASON AND MID SEASON STATS) #####

#CALCULATE FINAL PROBABILITIES FOR ONE MATCH
def final_match_prob(hteam, ateam):
    WEIGHTING = factor_weights()        #get weightings for each factor
    
    #get probabilities based on each factor
    factor1 = match_result_prob(STRENGTH_RATINGS[hteam], STRENGTH_RATINGS[ateam])   #preseason odds factor
    factor2 = match_result_prob1(hteam, ateam)  #record factor
    factor3 = match_result_prob2(hteam, ateam)  #form factor
    
    #only include preseason odds if either team has played a game
    if TEAM_STATS[hteam][2]==0 or TEAM_STATS[ateam][2]==0:
        return factor1
    
    #final match probabilities
    hteam_win = factor1[0] * WEIGHTING[0] + factor2[0]*WEIGHTING[1] + factor3[0]*WEIGHTING[2]
    draw = factor1[1]*WEIGHTING[0] + factor2[1]*WEIGHTING[1] + factor3[1]*WEIGHTING[2]
    ateam_win = factor1[2]*WEIGHTING[0]+ factor2[2]*WEIGHTING[1]+ factor3[2]*WEIGHTING[2]
    
    return [hteam_win, draw, ateam_win]

#print(final_match_prob('Liverpool FC', 'Arsenal FC'))

#DECIDE RESULT OF MATCH BASED ON PROBABILITY
def simulate_result(hteam, ateam):
    probabilities = final_match_prob(hteam, ateam)  #get match probabilities

    outcomes = [hteam + ' wins', "Draw", ateam + " wins"]   #possible outcome
    result = random.choices(outcomes, weights=probabilities, k=1)[0]    #capture result
    
    return result

#print(simulate_result("Liverpool FC", "Arsenal FC"))


#UPDATES TABLE BASED ON MATCH RESULTS (ranking not updated here)

#update team's form 
def update_form(team, outcome):  
    old_form = TEAM_STATS[team][4]
    new_form = outcome + old_form       #add new result
    TEAM_STATS[team][4] = new_form[:5]  # keep 5 latest results

#update table after each match result (uses update_form)
def update_table(hteam, ateam, result):
    
    #update predicted league table after each result
    if result == hteam + ' wins':
        TEAM_STATS[hteam][1] += 3      #3 points for winning team
        TEAM_STATS[hteam][2] += 1      #1 more game played
        TEAM_STATS[hteam][3][0] += 1     #1 more win
        
        TEAM_STATS[ateam][2] += 1      #1 more game played
        TEAM_STATS[ateam][3][2] += 1      #1 more loss
        
        update_form(hteam, 'W')
        update_form(ateam, 'L')
    
    elif result == "Draw":
        TEAM_STATS[hteam][1] += 1      #1 point for draw
        TEAM_STATS[ateam][1] += 1
        TEAM_STATS[hteam][2] += 1      #1 more game played
        TEAM_STATS[ateam][2] += 1
        TEAM_STATS[hteam][3][1] += 1      #1 more draw
        TEAM_STATS[ateam][3][1] += 1
        
        update_form(hteam, 'D')
        update_form(ateam, 'D')
    
    else:
        TEAM_STATS[ateam][1] += 3      #3 points for winning team
        TEAM_STATS[ateam][2] += 1      #1 more game played
        TEAM_STATS[ateam][3][0] += 1     #1 more win
        
        TEAM_STATS[hteam][2] += 1      #1 more game played
        TEAM_STATS[hteam][3][2] += 1      #1 more loss
        
        update_form(hteam, 'L')
        update_form(ateam, 'W')


#update_rank()
#printer.pprint(TEAM_STATS)

##### HANDLE ALREADY PLAYED GAMES #####
def process_matches():
    url = 'https://api.football-data.org/v4/competitions/PL/matches'
    params = {'season': 2025}
    response = requests.get(url, headers=headers, params=params)

    played_matches = {}     
    unplayed_matches = []   
    
    matches = response.json().get('matches', [])
    for match in matches:
        home = match['homeTeam']['name']
        away = match['awayTeam']['name']
        status = match['status']
        score = match['score']['fullTime']

        match_key = f"{home} vs {away}"

        #if games already finished
        if status == "FINISHED":
            home_score = score['home']
            away_score = score['away']
            
        #add game results
            if home_score > away_score:
                result = f"{home} wins"
            elif away_score > home_score:
                result = f"{away} wins"
            else:
                result = "Draw"

            played_matches[match_key] = result
        else:
            unplayed_matches.append((home + " vs " + away))

    return played_matches, unplayed_matches

#printer.pprint(process_matches())
PLAYED_MATCHES = process_matches()[0]       #dictionary of finished games
#print(PLAYED_MATCHES)
LIST_OF_PLAYED_MATCHES = list(PLAYED_MATCHES.keys())

##### SIMULATE LEAGUE #####
def simulate_league():
    
    #simulate all matches
    for i in range(len(EPL_TEAMS)):
        for j in range(i+1, len(EPL_TEAMS)):
            team1 = EPL_TEAMS[i]
            team2 = EPL_TEAMS[j]
            
            #simulate matches if not already played
            if team1 + ' vs ' + team2 not in LIST_OF_PLAYED_MATCHES:
                game1_result = simulate_result(team1, team2)
                PREDICTED_RESULTS[team1 + ' vs ' + team2] = game1_result     #add result to results list
                update_table(team1, team2, game1_result)        #update table
                
            if team2 + ' vs ' + team1 not in LIST_OF_PLAYED_MATCHES:    
                game2_result = simulate_result(team2, team1)
                PREDICTED_RESULTS[team2 + ' vs ' + team1] = game2_result     #add result to results list
                update_table(team2, team1, game2_result)        #update table

simulate_league()

#printer.pprint(LIST_OF_PLAYED_MATCHES)  #prints all existing results
#printer.pprint(PREDICTED_RESULTS)      #prints all predicted results
#printer.pprint(TEAM_STATS)        #prints predicted table (ranking not updated)

##### UPDATES TEAM STANDINGS IN TABLE #####
def update_table():
    global TEAM_STATS

    # Sort teams by points (descending)
    sorted_table = sorted(TEAM_STATS.items(), key=lambda item: item[1][1], reverse=True)

    # Update rank and rebuild the table
    new_table = {}
    for rank, (team, data) in enumerate(sorted_table, start=1):
        data[0] = rank  # update rank at index 0
        new_table[team] = data
    TEAM_STATS = new_table
    
    return TEAM_STATS

update_table()
#print(TEAM_STATS)       #final table in dictionary

##### OPTION TO DISPLAY TABLE IN TERMINAL #####
def display_table():
    

    # Print the table in formatted columns
    print(f"{'Rank':<5} {'Team':<30} {'Pts':<5} {'P':<3} {'W':<3} {'D':<3} {'L':<3} {'Form'}")
    print("-" * 70)
    for team, data in TEAM_STATS.items():
        rank, pts, played, [wins, draws, losses], form = data
        print(f"{rank:<5} {team:<30} {pts:<5} {played:<3} {wins:<3} {draws:<3} {losses:<3} {form}")

display_table()

##### DISPLAY LEAGUE TABLE IN NEW WINDOW #####
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
    root.geometry("800x900")

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

    headers = ["Pos", "Logo", "Team", "Pts", "P", "W", "D", "L", "Form"]
    for col, h in enumerate(headers):
        tk.Label(scroll_frame, text=h, font=("Arial", 12, "bold"), borderwidth=1, relief="solid",
            bg="#d1d1d1", padx=8, pady=10).grid(row=0, column=col, padx=1, pady=1, sticky="nsew")

    # Sort by rank (index 0 in each stat list)
    sorted_table = sorted(table.items(), key=lambda x: x[1][0])

    logo_images = []  # Keep image references alive

    for i, (team, stats) in enumerate(sorted_table, start=1):
        bg_color = "#f9f9f9" if i % 2 == 0 else "white"
        rank, pts, played, (wins, draws, losses), form = stats

        tk.Label(scroll_frame, text=str(rank), borderwidth=1, relief="solid",
            bg=bg_color, padx=6, pady=10).grid(row=i, column=0, sticky="nsew")

        # Logo column
        logo_path = TEAM_LOGOS.get(team)
        if logo_path:
            img = Image.open(logo_path).resize((40, 45))
            img_tk = ImageTk.PhotoImage(img)
            logo_images.append(img_tk)
            tk.Label(scroll_frame, image=img_tk, borderwidth=1, relief="solid",
                bg=bg_color).grid(row=i, column=1, padx=1, pady=1)
        else:
            tk.Label(scroll_frame, text="N/A", borderwidth=1, relief="solid",
                bg=bg_color).grid(row=i, column=1, padx=1, pady=1)

        # Team name
        tk.Label(scroll_frame, text=team, borderwidth=1, relief="solid",
            bg=bg_color, padx=6, pady=10).grid(row=i, column=2, sticky="nsew")

        # Stats: Pts, P, W, D, L, Form
        values = [pts, played, wins, draws, losses, form]
        for j, val in enumerate(values, start=3):
            tk.Label(scroll_frame, text=str(val), borderwidth=1, relief="solid",
                bg=bg_color, padx=6, pady=10).grid(row=i, column=j, sticky="nsew")

    root.mainloop()

show_league_table(TEAM_STATS)


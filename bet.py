"""
bet.py - A simple bot made with python that will help you to predict the result of a football game using the SofaScore API

@ Bastien Lasorne - 2021

v1.0

data from api.sofascore.com

https://api.sofascore.com/api/v1/config/unique-tournaments/EN/football => Obtenir la liste des championnats
https://api.sofascore.com/api/v1/unique-tournament/<championship_id>/seasons => Obtenir les ID des différentes saisons de Premier League
https://api.sofascore.com/api/v1/unique-tournament/<championship_id>/season/<id_season>/standings/total => Obtenir les informations sur le championnat de Premier League
https://api.sofascore.com/api/v1/unique-tournament/17/season/29415/standings/home => Obtenir des informations sur les matchs joués à domicile en Premier League
https://api.sofascore.com/api/v1/unique-tournament/17/season/29415/standings/away => Obtenir des informations sur les matchs joués à l'extérieur en Premier League
https://api.sofascore.com/api/v1/unique-tournament/17/season/29415/rounds => Obtenir le round actuel
https://api.sofascore.com/api/v1/unique-tournament/17/season/29415/team-events/total => Obtenir l'historique des matchs de chaques équipes
https://api.sofascore.com/api/v1/unique-tournament/17/season/29415/events/round/27 => Voir les matchs pour une journée
https://api.sofascore.com/api/v1/event/8897086/odds/1/all => Obtenir les côtes pour le match

Objectif : Trouver le nombre d'appels d'API possible par heures
Envoyer un mail tout les matins avec les analyses du jour dans les 5 gros championnats
Envoyer les bons plans (comparaison côte/réalité, gros % de victoire, gros % d'avoir peu de buts, etc...)
Envoyer dans ce mail un lien qui permet de parier en simple tous les bons plan de manière automatique sur le raspberry PI

"""

import requests
import math
from datetime import date, datetime
import time

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"}

def get_championship(*args):
    if args:
        champ_id = args[0]
    else:
        print("Load the list of championships...")
        # List All the most popular championships
        championships = requests.get("https://api.sofascore.com/api/v1/config/unique-tournaments/EN/football", headers=headers).json()
        i = 1
        for championship in championships["uniqueTournaments"]:
            print("{}. {} - {}".format(i, championship["name"], championship["category"]["flag"]))
            i+=1
        print("\nWhich championship do you want to bet on ?")
        champ_id = input("=> ")
        # Find the chosen championship id
        champ_id = championships["uniqueTournaments"][int(champ_id)-1]["id"]
    seasons = requests.get("https://api.sofascore.com/api/v1/unique-tournament/{}/seasons".format(champ_id), headers=headers).json() # Find the actual season id for the chosen championship
    actual_season_id = seasons["seasons"][0]["id"]
    return champ_id, actual_season_id

def proba(occurence, goal, local_goal_expected, visitor_goal_expected, local_name, visitor_name):
    home_proba_goal = (float(local_goal_expected)**goal)*(math.exp(-float(local_goal_expected)))/math.factorial(int(goal))
    visitor_proba_goal = (float(visitor_goal_expected)**goal)*(math.exp(-float(visitor_goal_expected)))/math.factorial(int(goal))
    print("Probability for {} to score {} goals : {}".format(local_name, goal, home_proba_goal))
    print("Probability for {} to score {} goals : {}\n".format(visitor_name, goal, visitor_proba_goal))
    return(home_proba_goal, visitor_proba_goal)

def score_probability(home_goal, away_goal):
    return home_goal * away_goal

def championship_data(championship, season):
    print("Load home's data...")
    home_data = requests.get("https://api.sofascore.com/api/v1/unique-tournament/{}/season/{}/standings/home".format(championship, season), headers=headers).json()
    print("Load away's data...")
    away_data = requests.get("https://api.sofascore.com/api/v1/unique-tournament/{}/season/{}/standings/away".format(championship, season), headers=headers).json()
    print("Load informations about the current round")
    round_data = requests.get("https://api.sofascore.com/api/v1/unique-tournament/{}/season/{}/rounds".format(championship, season), headers=headers).json()
    current_round = round_data["currentRound"]["round"]
    current_round_data = requests.get("https://api.sofascore.com/api/v1/unique-tournament/{}/season/{}/events/round/{}".format(championship, season, current_round), headers = headers).json()
    print("Calculating the average number of goals scored and conceded per home and away game")
    home_matches_played = 0
    home_goal_scored = 0
    home_goal_conceded = 0
    away_matches_played = 0
    away_goal_scored = 0 
    away_goal_conceded = 0
    for team in home_data["standings"][0]["rows"]:
        home_matches_played += team["matches"]
        home_goal_scored += team["scoresFor"]
        home_goal_conceded += team["scoresAgainst"]
    for team in away_data["standings"][0]["rows"]:
        away_matches_played += team["matches"]
        away_goal_scored += team["scoresFor"]
        away_goal_conceded += team["scoresAgainst"]
    average_home_goal_scored = home_goal_scored / home_matches_played
    average_home_goal_conceded = home_goal_conceded / home_matches_played
    average_away_goal_scored = away_goal_scored / away_matches_played
    average_away_goal_conceded = away_goal_conceded / away_matches_played
    
    print("Average number of goals scored at home in this league : {}".format(average_home_goal_scored))
    print("Average number of goals conceded at home in this league : {}".format(average_home_goal_conceded))
    print("Average number of goals scored away in this league : {}".format(average_away_goal_scored))
    print("Average number of goals scored away in this league : {}".format(average_away_goal_scored))

    number_of_matches = 0
    # Do the predictions for the games that are not already played
    print("")
    print("Round {}".format(current_round))

    global_probability = []

    for game in current_round_data["events"]:
        match_id = game["id"]
        print("============================================================\n")
        print("{} - {} => {}".format(game["homeTeam"]["name"], game["awayTeam"]["name"], str(game["homeScore"]["current"]) + "-" + str(game["awayScore"]["current"]) if game["status"]["type"] == "finished" else "Not already played"))
        print("")
        if game["status"]["type"] == "notstarted":
            hometeam_id = game["homeTeam"]["id"]
            awayteam_id = game["awayTeam"]["id"]
            hometeam_name = game["homeTeam"]["name"]
            awayteam_name = game["awayTeam"]["name"]
            for team in home_data["standings"][0]["rows"]:
                if team["team"]["id"] == hometeam_id:
                    average_goal_scored_by_home_team = team["scoresFor"] / team["matches"]
                    average_goal_conceded_by_home_team = team["scoresAgainst"] / team["matches"]
                    print("Average Goal scored by {} at home : {}".format(hometeam_name, average_goal_scored_by_home_team))
                    print("Average Goal scored by {} at home : {}".format(hometeam_name, average_goal_conceded_by_home_team))
                    print("")
                if team["team"]["id"] == awayteam_id:
                    average_goal_scored_by_away_team = team["scoresFor"] / team["matches"]
                    average_goal_conceded_by_away_team = team["scoresAgainst"] / team["matches"]
                    print("Average Goal scored by {} away : {}".format(awayteam_name, average_goal_scored_by_away_team))
                    print("Average Goal scored by {} away : {}".format(awayteam_name, average_goal_conceded_by_away_team))
                    print("")

            home_attack_strength = float(average_goal_scored_by_home_team) / float(average_home_goal_scored)
            away_attack_strength = float(average_goal_scored_by_away_team) / float(average_away_goal_scored)
            home_defense_strength = float(average_goal_conceded_by_home_team) / float(average_home_goal_conceded)
            away_defense_strength = float(average_goal_conceded_by_away_team) / float(average_away_goal_conceded)

            print("{} Attack Strength : {}".format(hometeam_name, home_attack_strength))
            print("{} Attack Strength : {}".format(game["awayTeam"]["name"], away_attack_strength))

            print("")

            print("{} Defense Strength : {}".format(hometeam_name, home_defense_strength))
            print("{} Attack Strength : {}".format(awayteam_name, away_defense_strength))

            print("")

            home_goal_expectancy = float(home_attack_strength) * float(away_defense_strength) * float(average_home_goal_scored)

            away_goal_expectancy = float(away_attack_strength) * float(home_defense_strength) * float(average_away_goal_scored)

            print("{}'s goal expectancy : {}".format(hometeam_name, home_goal_expectancy))
            print("{}'s goal expectancy : {}".format(awayteam_name, away_goal_expectancy))

            ts = time.gmtime(game["startTimestamp"])

            probability = {
                "league_name": game["tournament"]["name"],
                "home_team_name": hometeam_name,
                "away_team_name": awayteam_name,
                "game_start": time.strftime("%Y-%m-%d %H:%M:%S", ts),
                "home_team_goal" : {},
                "visitor_team_goal": {},
                "score_probability": {},
                "result_proba": {
                    "home_victory": 0,
                    "draw": 0,
                    "away_victory": 0,
                }
            }

            # Get the current odds by the bookmakers
            bookmakers_odds = requests.get("https://api.sofascore.com/api/v1/event/{}/odds/1/all".format(match_id), headers=headers).json()

            home_victory_odds = 1 + eval(bookmakers_odds["markets"][0]["choices"][0]["fractionalValue"])
            draw_odds =  1 + eval(bookmakers_odds["markets"][0]["choices"][1]["fractionalValue"])
            away_victory_odds =  1 + eval(bookmakers_odds["markets"][0]["choices"][2]["fractionalValue"])

            probability["odds"] = [home_victory_odds, draw_odds, away_victory_odds]

            occurence = 6

            for i in range(occurence):
                home_goal, visitor_goal = proba(occurence, i, home_goal_expectancy, away_goal_expectancy, hometeam_name, awayteam_name)
                probability["home_team_goal"][i] = home_goal
                probability["visitor_team_goal"][i] = visitor_goal

            for home_goal in range(occurence):
                for away_goal in range(occurence):
                    score_proba = score_probability(probability["home_team_goal"][home_goal], probability["visitor_team_goal"][away_goal])
                    probability["score_probability"]["{}-{}".format(home_goal, away_goal)] = score_proba
                    if home_goal > away_goal:
                        probability["result_proba"]["home_victory"] += score_proba
                    elif away_goal > home_goal:
                        probability["result_proba"]["away_victory"] += score_proba
                    else:
                        probability["result_proba"]["draw"] += score_proba

            print("")
            print("=> Probability for {} to win : {} % \t\t Odds : {}".format(hometeam_name, probability["result_proba"]["home_victory"]*100, 1/probability["result_proba"]["home_victory"] if probability["result_proba"]["home_victory"] != 0 else "unestimated"))
            print("Bookmakers' odds : {}".format(probability["odds"][0]))
            print("=> Probability of a draw : {} % \t\t Odds : {}".format(probability["result_proba"]["draw"]*100, 1/probability["result_proba"]["draw"] if probability["result_proba"]["draw"] != 0 else "unestimated"))
            print("Bookmakers' odds : {}".format(probability["odds"][1]))
            print("=> Probability for {} to win : {} % \t\t Odds : {}".format(awayteam_name, probability["result_proba"]["away_victory"]*100, 1/probability["result_proba"]["away_victory"] if probability["result_proba"]["away_victory"] != 0 else "unestimated"))
            print("Bookmakers' odds : {}".format(probability["odds"][2]))

            # Sort the probable score by probability
            sorted_proba = {}
            sorted_keys = sorted(probability["score_probability"], key=probability["score_probability"].get, reverse=True)

            for w in sorted_keys:
                sorted_proba[w] = probability["score_probability"][w]

            probability["score_probability"] = sorted_proba

            print("\nTop 5 probable scores : ")
            position = 1
            for x in list(sorted_proba)[0:5]:
                print("{}. \t {} \t Probability : {} %".format(position, x, sorted_proba[x]*100))
                position+=1

            if date.today() == datetime.strptime(probability["game_start"], '%Y-%m-%d %H:%M:%S').date():
                global_probability.append(probability)

        print("============================================================\n")
    return global_probability

def send_mail(email_address):
    print("I have to send an email to {}".format(email_address))

def main(*args, **kwargs):
    print("Welcome to our bet program\n")
    if args:
        champ_id, actual_season_id = get_championship(args[0])
    else:
        champ_id, actual_season_id = get_championship()
    return championship_data(champ_id, actual_season_id)
    # Send an email if we get the argument "send_mail" equal to True
    # if "send_mail" in kwargs:
    #     if kwargs["send_mail"] == True:
    #         if not "email_address" in kwargs:
    #             print("You forgot to give us an email address")
    #         else:
    #             send_mail(kwargs["email_address"])
    
if __name__ == "__main__":
    main()
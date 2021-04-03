"""
automation.py - An automation of the bet.py program which sends me an email with the analyzes of the day as well as good plans.

@ Bastien Lasorne - 2021

v1.0
"""
import bet
from datetime import datetime, timedelta # Execute the program each day at the same our
from threading import Timer
import time
import schedule
import os

import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# # For this laptop
# x = datetime.today()
# # y = x.replace(day=x.day, hour=0, minute=30, second=0, microsecond=0) + timedelta(days=1)
# y = x.replace(day=x.day, hour=0, minute=0, second=0, microsecond=0)
# delta_t=y-x

# secs = delta_t.total_seconds() # On exprime le temps entre chaques répétitions du programme en secondes

addresses = [os.getenv("EMAIL1"), os.getenv("EMAIL2")]

def send_mail(**kwargs):
    from_addr = os.getenv("MAINEMAIL")
    day_matches = 0
    for league in all_stats:
        day_matches += len(league)
    email_address = kwargs["email_address"]
    mail_object="{}".format(str(day_matches) + " match{} sur {} parier aujourd'hui !".format("s" if day_matches > 1 else "", "lesquels" if day_matches > 1 else "lequel") if day_matches > 0 else "Aucuns match au programme aujourd'hui...")
    if day_matches > 0:
        content = "Bonne nouvelle !<br/>Nous avons aujourd'hui {} match{} sur {} nous pouvons vous conseiller. Jetez-y un coup d'oeil !<br/>".format(day_matches, "s" if day_matches > 1 else "", "lesquels" if day_matches > 1 else "lequel")
    else:
        content = "Il n'y a malheureusement pas de matchs sur lesquels parier aujourd'hui...<br/>Rendez-vous demain pour obtenir nos analyses du jour."
    for league in all_stats:
        day_matches += len(league)
        if len(league) > 0:
            league_content = "<br/>{} : {} match{}<br/>".format(league[0]["league_name"],len(league), "s" if len(league) > 1 else "")
            content += league_content
            for i in league:
                match_content = "=================================<br/>"
                match_content += "<bold>{} - {}<br/>{}<br/></bold>".format(i["home_team_name"], i["away_team_name"], i["game_start"])
                match_content += "<br/><bold>Probabilité que {} gagne : {} % </bold>&emsp; Côte estimé : {}<br/>Côte des bookmakers : {}<br/>".format(i["home_team_name"], i["result_proba"]["home_victory"]*100,  1/i["result_proba"]["home_victory"] if i["result_proba"]["home_victory"] != 0 else "unestimated", i["odds"][0])
                match_content += "<br/><bold>Probabilité qu'il y ait match nul : {} % </bold>&emsp; Côte estimé : {}<br/>Côte des bookmakers : {}<br/>".format(i["result_proba"]["draw"]*100,  1/i["result_proba"]["draw"] if i["result_proba"]["draw"] != 0 else "unestimated", i["odds"][1])
                match_content += "<br/><bold>Probabilité que {} gagne : {} % </bold>&emsp; Côte estimé : {}<br/>Côte des bookmakers : {}<br/>".format(i["away_team_name"], i["result_proba"]["away_victory"]*100,  1/i["result_proba"]["away_victory"] if i["result_proba"]["away_victory"] != 0 else "unestimated", i["odds"][2])
                match_content += "<br/><bold>Top 5 scores probables : </bold><br/>"
                position = 1
                for x in list(i["score_probability"])[0:5]:
                    match_content += "{}. &emsp; {} &emsp; Probabilité : {} %<br/>".format(position, x, i["score_probability"][x]*100)
                    position+=1
                match_content += "<br/>=================================<br/>"
                content += match_content

    # port = 465  # For SSL
    password = os.getenv("PASSWORD")
 
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("lespronosdebastien@gmail.com",password)

    #To Create Email Message in Proper Format
    msg = MIMEMultipart()
    #Setting Email Parameters
    msg['From'] = from_addr
    msg['To'] = email_address
    msg['Subject'] = mail_object

    #Add Message To Email Body
    msg.attach(MIMEText(content, 'text'))

    # problems = server.sendmail(from_addr, email_address, msg.encode("utf-8"))
    server.send_message(msg)
    server.quit()
    

def call_bet():
    # Call bet with the numero of the league that we want, the option send_mail and the email_address
    global all_stats
    all_stats = []
    premier_league = bet.main(17)
    all_stats.append(premier_league)
    #time.sleep(60*60*2)
    liga = bet.main(8)
    all_stats.append(liga)
    #time.sleep(60*60*2)
    bundes = bet.main(35)
    all_stats.append(bundes)
    #time.sleep(60*60*2)
    seria_a = bet.main(23)
    all_stats.append(seria_a)
    # time.sleep(60*60*2)
    ligue_1 = bet.main(34)
    all_stats.append(ligue_1)
    # print(all_stats)
    for address in addresses:
        send_mail(email_address=address)

# For this laptop 
# t = Timer(secs, call_bet)
# t.start()


#------------Proper Loop----------------
schedule.every().day.at("07:59").do(call_bet)

while True:
    schedule.run_pending()
    time.sleep(60) # wait one minute

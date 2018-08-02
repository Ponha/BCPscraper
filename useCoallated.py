import datetime
import dateparser
import json
from collections import defaultdict

def filterEvents(events, fromDate=datetime.date(1,1,1), toDate=datetime.date(9000,1,1), minRounds=0, maxRounds=100):
    if (fromDate == datetime.date(1,1,1)
    and toDate == datetime.date(9000,1,1)
    and minRounds == 0
    and maxRounds == 100):
        return events
    else:
        return [x for x in events
                if dateparser.parse(x["date"]).date()>fromDate
                and dateparser.parse(x["date"]).date()<toDate
                and x["rounds"] >= minRounds
                and x["rounds"] <= maxRounds
        ]

def itcFaction(data, factKey):
    #print(factKey)
    data = data.strip()
    for k, v in factKey.items():
        if data in v:
            #print("hit")
            return k
    #print("miss")
    print("Unkown faction: " + data)
    return data

def numberOfGamesPerFaction(events, fromDate=datetime.date(1,1,1), toDate=datetime.date(9000,1,1)):
    events = filterEvents(events, fromDate, toDate)
    factKey = {}
    with open("factKey.json", "r") as f:
        factKey = json.load(f)
    factionGames = {}
    for event in events:
        for player in event["results"]:
            nrOfGames = len(player["wins"]) + len(player["draws"]) + len(player["losses"])
    
            try:
                factionGames[itcFaction(player["faction"], factKey)] += nrOfGames
            except:
                factionGames[itcFaction(player["faction"], factKey)] = nrOfGames
    return factionGames

def winRatioPerFaction(events, fromDate=datetime.date(1,1,1), toDate=datetime.date(9000,1,1)):
    events = filterEvents(events, fromDate, toDate)
    with open("factKey.json", "r") as f:
        factKey = json.load(f)
    factionWinrate = {}
    for event in events:
        for player in event["results"]:
            wins = len(player["wins"])
            losses = len(player["losses"])
            itcFact = itcFaction(player["faction"], factKey)
            if itcFact in factionWinrate.keys():
                factionWinrate[itcFact][0] += wins
                factionWinrate[itcFact][1] += losses
            else:
                factionWinrate[itcFact] = [wins, losses]
            #factionWinrate[itcFaction(player["faction"], factKey)] + (wins, losses)
             #try:
            #factionWinrate[itcFaction(player["faction"], factKey)][0] += wins
            #factionWinrate[itcFaction(player["faction"], factKey)][1] += losses
            #except:
            #    factionWinrate[itcFaction(player["faction"], factKey)] = (wins, losses)
    byPercent={}    
    for k, v in factionWinrate.items():
        byPercent[k] = 100 * (v[0]/(v[0]+v[1]))
    return byPercent

def representationPerFaction(gamesPerFaction):
    totalGames = 0
    percentRepresentation = {}
    for k, v in gamesPerFaction:
        totalGames += v
    for k, v in gamesPerFaction:
        percentRepresentation[k] = 100 * (v/totalGames)
    return percentRepresentation
        
if __name__ == "__main__":
    print ("run useCoallated as __main__")
    events = []
    with open("eventsCoallated.json", "r") as f:
        events = json.load(f)

    events = filterEvents(events, datetime.date(2018,7,1))
    
    gamesPerFaction = sorted(numberOfGamesPerFaction(events).items(), key=lambda x:x[1], reverse=True)
    winPerFaction = sorted(winRatioPerFaction(events).items(), key=lambda x:x[1], reverse=True)
    percentRepresentation = sorted(representationPerFaction(gamesPerFaction).items(), key=lambda x:x[1], reverse=True)

    
    print("\n Games played in total for factions: \n ==============================")
    for k, v in gamesPerFaction:
        print(k + ": " + str(v))
    print("\n Win ratio for factions: \n ==============================")        
    for k, v in winPerFaction:
        print(k + ": " + str(round(v,1)))
    print("\n Representation for factions (percent): \n ============================")
    for k, v in percentRepresentation:
        print(k + ": " + str(round(v,1)))
    

import requests
from bs4 import BeautifulSoup
import json

def scrapeEvent(url):
    print("request url is: " +url +"\n")
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')


    mydivs = soup.find("div", {"class": "event-list"})
    players = mydivs.find_all("li", recursive=False)

    list_of_players = []
    for player in players:
        playerDict = {
            #"placing" = 0,
            ##"name" = "0",
            #"itcPoints" = None,
            #"faction" = None,
            #"swissPoints" = None,
            #"record" = []
        }
        player_result = player.find("time")
        playerDict["placing"] = int(player_result.find("span", {"class": "placing"}).get_text())
        try:
            playerDict["itcPoints"] = float(player_result.find("span", {"class": "itcpts"}).get_text())
        except:
           # print(player.prettify())
           # print(playerDict)
            playerDict["itcPoints"] = 0.0
        playerInfo= player.find("div", {"class": "info"})
        #print("\n\n\n\n\n\n\n\n\n\n\n")
        try:
            playerDict["name"] = playerInfo.find("h2").find("span").get_text()
        except:
            playerDict["name"] = playerInfo.find("h2").get_text()
            #print(playerInfo.prettify())
            
        playerDict["faction"] = playerInfo.find("p").get_text().split("-")[0]
        playerDict["team"] = playerInfo.find("p").get_text().split("-")[1]
        playerScores = player.find("div", {"class": "scoresLabel"}).find("ul").find_all("li", recursive=False)
        playerDict["swissPoints"] = playerScores[0].get_text()
        playerDict["wins"] = []
        playerDict["losses"] = []
        playerDict["draws"] = []
        wins = playerScores[1].find_all("span", {"style": "color:green;"})
        losses = playerScores[1].find_all("span", {"style": "color:red;"})
        draws = playerScores[1].find_all("span", {"style": "color:yellow;"})
        for win in wins:
            playerDict["wins"].append(int(win.get_text()))
        for loss in losses:
            playerDict["losses"].append(int(loss.get_text()))
        for draw in draws:
            playerDict["draws"].append(int(draw.get_text()))
        list_of_players.append(playerDict)
    return list_of_players

if __name__ == "__main__":
    listOfPlayers = scrapeEvent("https://www.bestcoastpairings.com/r/1ved4krt")
    with open("workfile.json", 'w') as f:
        f.write(json.dumps(listOfPlayers, indent=4))

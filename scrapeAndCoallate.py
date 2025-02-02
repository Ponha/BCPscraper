import events
from scrape import scrapeEvent
import dateparser
import json
import datetime
import time



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

def writeToFile(text, filename, jsn=False):
    if not json:
        with open(filename, "w+") as f:
            f.write(text)
    elif jsn:
        with open(filename, "w+") as f:
            f.write(json.dumps(text, indent=4, default=str))

def already_scraped(alreadyScraped, event):
    for x in alreadyScraped:
        if event["eventId"] == x["eventId"]:
            return True
    return False

if __name__ == "__main__":
    with open("events.json", 'r') as f:
        events = json.load(f)
    with open("eventsCoallated.json", 'r') as f:
        alreadyScraped = json.load(f)
    events = filterEvents(events)#, datetime.date(2018,1,1))
    counter = 0
    total = len(events)
    for event in events:
        if not already_scraped(alreadyScraped, event):
            counter += 1 
            url = "https://www.bestcoastpairings.com/r/" + event["eventId"].split("/")[2]
            event["results"] = scrapeEvent(url)
            if event["results"]:
                alreadyScraped.append(event)
                print("scraped: " + str(counter) + " / " + str(total) + ", current id: " + event["eventId"])
                time.sleep(0.5)
            else:
                print("Event skipped, not yet reported")
    writeToFile(alreadyScraped, "eventsCoallated.json", True)

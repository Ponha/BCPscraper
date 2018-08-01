import requests
import os
import json
import webbrowser
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
from bs4 import BeautifulSoup

browser = webdriver.Chrome()

url = "https://www.bestcoastpairings.com/events"

browser.get(url)

#wait for table to load by id
delay = 5
try:
    myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'DataTables_Table_0')))
    print ("Page is ready!")
except TimeoutException:
    print ("Loading took too much time!")

select = Select(browser.find_element_by_id("date-picker"))
select.select_by_visible_text("Last Year")
select = Select(browser.find_element_by_xpath("//select[@id='date-picker']//following-sibling::select"))
select.select_by_visible_text("Warhammer 40k")

finnished = False
listOfEvents = []
nr=0

while not finnished:
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    tableBody = soup.find("tbody")
    for row in tableBody.find_all("tr", recursive=False):
        event={}
        columns = row.find_all("td", recursive=False)
        event["date"] = columns[0].get_text()
        event["eventName"] = columns[2].get_text()
        event["eventId"] = columns[2].find("a")['href']
        event["rounds"] = int(columns[4].get_text().split()[0])
        listOfEvents.append(event)
        nr = nr + 1
    next = browser.find_element_by_id("DataTables_Table_0_next")
    if "disabled" not in next.get_attribute("class"):
        next.click()
    else:
        finnished = True

#print(tableBody.prettify())
print(nr)
with open("events.json", "w") as f:
    f.write(json.dumps(listOfEvents, indent=4))

browser.close()




#print(browser.page_source)

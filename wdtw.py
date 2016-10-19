#!/usr/bin/env python3
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
import requests
import json
import re

SERVICE_ADDR = "twitter.com"
PROPERTY = "P2002"
OUTPUT_FILE = "test.txt"
OUTPUT_GOOD = "good.txt"

WORDS = ["museum", "museet", "muzeum", "museo"]

open(OUTPUT_FILE, 'w').close()
open(OUTPUT_GOOD, 'w').close()

url = "https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20DISTINCT%20%3Fmuseum%20%3FmuseumLabel%20%3Fwww%20%20WHERE%20%7B%0A%20%20%3Fmuseum%20wdt%3AP31%2Fwdt%3AP279*%20wd%3AQ33506%20.%0A%20%20%3Fmuseum%20wdt%3AP856%20%3Fwww.%0A%20%20%20%20OPTIONAL%20%7B%20%3Fmuseum%20wdt%3AP2002%20%3Fdummy0.%20%7D%0A%20%20FILTER(!BOUND(%3Fdummy0))%0A%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%2Cde%2Cfr%2Cpl%2Cru%2Cfi%2Cnl%22.%20%7D%0A%7D&format=json"


# r = requests.get(url)
# data = r.json()
# data = data["results"]["bindings"]


with open("query.json") as dataFile:
    data = json.load(dataFile)

print(len(data), "items")

for item in data:
    #if item["www"] == "http://pwnhc.ca/index.html":
    identifier = item["museum"].split("/")[-1]
    #print(item["www"])
    possibleMatches = []
    usernames = []
    url = item["www"]
    print(url)
    try:
        r = requests.get(url, timeout=10)
        print(r)
        soup = bs(r.text)
        allLinks = soup.find_all('a')
        for link in allLinks:
            address = link.get('href')
            parsed = urlparse(address)
            if parsed.netloc == SERVICE_ADDR:
                possibleMatches.append(parsed)
        possibleMatches = set(possibleMatches)
        for m in possibleMatches:
            if (m.query == ""): # this should remove links like twitter.com/search?q=
                x = re.sub(r'\W+', '', m.path)
                if len(x) > 1:
                    usernames.append(x)
        usernames = set(usernames)
        usernames = list(usernames)
        if len(usernames) == 1:
            line = identifier + "\t" + PROPERTY + "\t" + '"' + usernames[0] + '"' + "\n"
            if any(substring in usernames[0].lower() for substring in WORDS):
                where = OUTPUT_GOOD
            else:
                where = OUTPUT_FILE
            with open(where, "a") as myfile:
                print(line)
                myfile.write(line)
    except requests.exceptions.RequestException as e:
        pass




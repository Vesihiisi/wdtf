#!/usr/bin/env python3
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
import requests
import json
import re
import tweepy

SERVICE_ADDR = "twitter.com"
PROPERTY = "P2002"
OUTPUT_FILE = "test.txt"
OUTPUT_GOOD = "good.txt"
OUTPUT_MATCH = "match.txt"

WORDS = ["musee", "museum", "museo", "muzeum"]

open(OUTPUT_FILE, 'w').close()
open(OUTPUT_GOOD, 'w').close()
open(OUTPUT_MATCH, 'w').close()

with open('config.json', 'r') as f:
    config = json.load(f)

auth = tweepy.OAuthHandler(config["consumer_token"], config["consumer_secret"])
auth.set_access_token(config["access_token"], config["access_token_secret"])

api = tweepy.API(auth)

url = "https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=SELECT%20DISTINCT%20%3Fmuseum%20%3FmuseumLabel%20%3Fwww%20%20WHERE%20%7B%0A%20%20%3Fmuseum%20wdt%3AP31%2Fwdt%3AP279*%20wd%3AQ33506%20.%0A%20%20%3Fmuseum%20wdt%3AP856%20%3Fwww.%0A%20%20%20%20OPTIONAL%20%7B%20%3Fmuseum%20wdt%3AP2002%20%3Fdummy0.%20%7D%0A%20%20FILTER(!BOUND(%3Fdummy0))%0A%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%2Cde%2Cfr%2Cpl%2Cru%2Cfi%2Cnl%22.%20%7D%0A%7D&format=json"

def getTwitterInfo(username):
    user = api.get_user(username)
    finalUrl = requests.get(user.url)
    return finalUrl.url

def urlMatch(url1, url2):
    parsed1 = urlparse(url1)
    parsed2 = urlparse(url2)
    if parsed1.netloc + parsed1.path == parsed2.netloc + parsed2.path:
        return True
    else:
        return False

r = requests.get(url)
data = r.json()
data = data["results"]["bindings"]


# with open("query.json") as dataFile:
#     data = json.load(dataFile)

print(len(data), "items")

for item in data:
    identifier = item["museum"]["value"].split("/")[-1]
    url = item["www"]["value"]
    possibleMatches = []
    usernames = []
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
            try:
                urlFromProfile = getTwitterInfo(usernames[0])
                line = identifier + "\t" + PROPERTY + "\t" + '"' + usernames[0] + '"' + "\n"
                if any(substring in usernames[0].lower() for substring in WORDS):
                    where = OUTPUT_GOOD
                elif urlMatch(urlFromProfile, url):
                    where = OUTPUT_MATCH
                else:
                    where = OUTPUT_FILE
                with open(where, "a") as myfile:
                    print(line)
                    myfile.write(line)
            except Exception as e:
                pass
    except requests.exceptions.RequestException as e:
        pass




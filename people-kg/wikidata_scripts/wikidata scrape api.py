# -*- coding: utf-8 -*-
"""
Created on Sun Feb  5 21:27:01 2023

@author: breeb
"""

import requests
import json


##get group identifiers
search_terms = ["Yoruba people", "Igbo people", "Kanuri people", "Ijaw people", "Ogbe tribe", "Tiv people", "Ibibio people", "Fulani", "Edo people"]
group_ids = []

for search_term in search_terms:
    response = requests.get("https://www.wikidata.org/w/api.php", params={
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "type": "item",
        "limit": "1",
        "search": search_term
    })
    data = response.json()
    
    if len(data["search"]) > 0:
        group_id = data["search"][0]["id"]
        group_ids.append(group_id)
    else:
        print(f"No results found for search term: {search_term}")




##Scrape relevant groups
query = """
SELECT DISTINCT ?group ?groupLabel ?alsoKnownAs ?instanceOf ?nativeLanguage ?country ?locatedIn ?religionOrWorldview ?hasParts
WHERE {{
  VALUES ?group {{ {group_values} }}
  ?group wdt:P31 wd:Q4167410;
    rdfs:label ?groupLabel.
  OPTIONAL {{ ?group wdt:P1448 ?alsoKnownAs }}
  OPTIONAL {{ ?group wdt:P31 ?instanceOf }}
  OPTIONAL {{ ?group wdt:P1399 ?nativeLanguage }}
  OPTIONAL {{ ?group wdt:P17 ?country }}
  OPTIONAL {{ ?group wdt:P131 ?locatedIn }}
  OPTIONAL {{ ?group wdt:P140 ?religionOrWorldview }}
  OPTIONAL {{ ?group wdt:P527 ?hasParts }}
  FILTER (LANG(?groupLabel) = "en")
}}
GROUP BY ?group ?groupLabel ?alsoKnownAs ?instanceOf ?nativeLanguage ?country ?locatedIn ?religionOrWorldview ?hasParts
ORDER BY ?groupLabel

""".format(group_values=' '.join(f'wd:{group_id}' for group_id in group_ids))

url = "https://query.wikidata.org/sparql"

response = requests.post(url, data={"query": query, "format": "json"})
data = response.json()
if "results" in data and "bindings" in data["results"] and len(data["results"]["bindings"]) > 0:
    results = data["results"]["bindings"]
    # Process the results
else:
    print("No results found in the query")

    
 ##make json file
response = requests.post(url, data={"query": query, "format": "json"})
data = response.json()

with open("data.json", "w") as f:
    json.dump(data, f)

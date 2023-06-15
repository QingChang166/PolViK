query = """
SELECT ?LanguageName ?CountryName ?AdminUnitName WHERE {
  ?subject rdfs:label "Igbo people"@en ;
      wdt:P31 ?isA ;
      wdt:P103 ?nativeLanguage ;
      wdt:P17 ?Country ;
      wdt:P131 ?AdminUnit .
  ?nativeLanguage rdfs:label ?LanguageName .
  ?Country rdfs:label ?CountryName .
  ?AdminUnit rdfs:label ?AdminUnitName .
  filter(lang(?LanguageName) = "en") .
  filter(lang(?CountryName) = "en") .
  filter(lang(?AdminUnitName) = "en") .
}
"""

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

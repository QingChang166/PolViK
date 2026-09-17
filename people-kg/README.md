# Country Files

Knowledge graphs for countries in subSaharan Africa


## Data Sources

| Feature        | Description                           | Sources             
|----------------|---------------------------------------|----------------------------------------:|
|  EthnicGroup   |    A self-identified identity group with common historical, cultural, linguistic, or religious     characteristics.                               |    Ethnologue, CIA Factbook, Joshua Project,  World Directory of Minorities and Indigenous People, Wikidata, Wikipedia                                   | 
| LinguisticGroup   |    Language family, may include dialects and variants                                 |     Ethnologue, Wikidata, Wikipedia                                  | 
| Religion      |       System of beliefs, practices and values.                                   |        Ethnologue, Joshua Project, Wikidata, Wikipedia                                | 
| IdeologicalGroup |             A specific set of beliefs about social, cultural, economic and political   issues.                     |                                        |
| PoliticalParty  |                                      |                                        | 
| ArmedNonGovernmentalOrganizedGroup |                   |                                        | Armed Group Dataset, ACLED, UCDP, Wikidata, Wikipedia


## Attributes

* **EthnicGroup**
  - stringTokens: 
  - wikidataQnode:
  - languagesMostSpoken:
  - religionsMostPracticed:
  - livesIn:
* **PoliticalParty**
  - stringTokens:
  - wikidataQnode:
  - associatedEthnicGroup:
  - associatedReligion
  - yearsActiveasParty:
* **armedNonGovernmentalOrganizedGroup**
  - stringTokens:
  - originCountry:
  - regionsMostActive:
  - associatedReligion:
  - associatedEthnicGroup:
  - groupType:
  - wikidataQnode:
  - ideologicalOrientation:
  - SpellConceptPath: 
* **linguisticGroup**
  - stringTokens:
  - wikidataQnode:
  - livesIn:
  - associatedethnicgroup:

# Observation Spells
Knowledge graphs for the temporal and spatial presence of armed groups in the country files.

## Data Sources
UCDP

## Attributes

* **UCDP Events**
  - spell_start:
  - spell_end:
  - locationConceptPath:
  - groupConceptPath:
  - SourceOfInfo:
  - DateOfInfo”:
  - coder:















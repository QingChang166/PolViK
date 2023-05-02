# TrIAD Knowledge Graph Ontology and Use

version: 0.0.1
author: Colaresi

In this repository we organize the *tokens*, *concepts*, *attributes*, and *relations* that comprise the knowledge graph for the TrIAD project. The goal of this sub-component of the project is to leverage qualitative knowledge about cases as well as the process that generates conflict more generally -- including ethnic, linguistic, religious, and national horizontal inequalities --  as well as external data sources -- specifically Wikidata -- to provide the facilities to flexibly aggregate, divide, and connect mentions of perpetrators and victims (and sources of information) for further analysis and comparison. 

We define the following components of our ontology:

- *tokens* -- These are strings of character sequences that can be detected in the text of human rights reports and other source documents. They may be ambiguous as to their meaning (eg "English" could refer to a person, a language, or a muffin). It is not the point of this sub-component of the project to disambiguate *tokens*, thus one token can be associated with multiple *concepts*, see below for more information on this. Note also that *tokens* can and often are multi-word expressions (mwe) and hence include spaces. 

- *concepts* -- These represent the underlying shared meaning of *tokens* (eg "person" and "human" both refer to our *concept* or `person`) or the shared part of the meaning of multiple *concepts* (eg `rebelGroup` and `governmentGroup` are both an example of an `organizedGroup`). In natural language concepts can have nearly multifareous meanings and overlaps, we use the minimum number and complexity of *concepts* to capture horizontal inequalities, conflict processes, and rights protections and violations. 

- *attributes* -- A *concept* for have various attributes. Two optional attributes are:
    - `stringTokens` which map that *concept* to a list/sequence of *tokens*
    - `wikiDataID` which maps that *concept* to a Wikidata unique identifier that we can use to move across our limited, specific knowledge graph to the vast Wikidata KG.

    Other attributes can be added, but they should be added only sparsely. Where possible, external information should be added from Wikidata. 

- *relations* -- These are connections/directed edges between *concepts*. They represent is-a relations moving from general concept (the parent) to a more specific conflict (the child). Where these is ambiguity about the parent, the most general parent should be selected that makes sense. The relations (`organizedGroup`, `rebelGroup`) represents the relationship that the `rebelGroup` concept is an `organizedGroup`. 


When new perpetrators, victims, or sources of information are detected in the source texts by PULSAR, they need to be added to the KG. In the future, we would like to automate this process, but currently we do this manually. 

Once perpetrator, victim, or sources of information *tokens* in the text have been identified and their appropriate concept in the knowledge graph has been identified (eg "hausa people" is identified by PULSAR as victims,  `hausaEthnicGroup` is the concept because this `concept` has the attribute `stringTokens` equal to a list that includes "Hausa people"). 

If we want to analyze the violations of the rights in a given country (or across countries) to the Hausa people across different mentions in the text, we can now use all of victims that link to that concept even if they were referred to by different *tokens*. Further, because `hausaEthnicGroup` has a relation that defines `ethnicGroup` as its parent, we can look at the differences in violations across different children of `ethnicGroup`, again within or across countries.


# Format

After some experimentation and testing, we will utilize a set of structured yaml files to enter and store our knowledge graph *tokens*, *concepts*, *attributes*, and *relations*. The files will be organized such that we first have two files that represent the *concepts* and *relations* that could apply to most/all countries around the world. We denote these `BaseConcepts.yaml` and `BaseRelations.yaml`. They are formatted such that:

- There is one `BaseConcepts.yaml` file that includes *concepts* with `stringTokens` attributes that record the associated a*tokens*. The format of the file should be a map (key -- value pair), with the outer key being `concepts` and the inner value holding another set of maps, with each individual inner map item (themselves a key -- value pair). Like so:
    ```
    concepts: # key: name of concept for instantiation, value a dict with at least key stringTokens holding a list
        people:
            stringTokens: ["people", "peoples", "human", "humans", "everyone", "population"]
            wikiDataID: 
        genderGroup:
            stringTokens: []  
            wikiDataID: 
    <snip>
    ```
     Note that the `stringTokens` attribute points to a list of string tokens. the wikiDataID is expected to point to a string.

- There is one `BaseRelations.yaml` file that includes *relations* between *concepts*. These are simply recorded as a map/dictionary with the outer key being `relations` that points to a value which is a sequence/list of 2-length tuples. Like so:
    ```
    relations: # parent concept, child concept, tuples
        - (ROOT, people)
        - (people, genderGroup)
        - (genderGroup, maleGender)
        - (genderGroup, femaleGender)  
    <snip>
    ```

- Each country gets there own named versions of *concepts* and *relations* files. Each country file should have the set of additional *concepts* (and thus *attributes*) and *relations* that if were to load both the `base*` files and the two country-specific files (encoding *concepts* and *relations* for that specific country), we should have the most important groups and actors for that country related to human rights and conflict processes (at a relatively low level of conceptual granularity). There will be many occasions where a *token* mentioned in a country report for country A, is already defined and assigned to a concept in country B's files and data. In these cases, if the group/person/meaning is different (eg Hausa people specifically in Nigeria versus Hausa people in Chad), then there should be entries in both countries concepts files. The names can be the same because the namespace for concepts is the file, hence `NigeriaConcepts::hausaEthnicGroup` is distinct from `ChadConcepts::hausaEthnicGroup`.

If, however, the actor mentioned is exactly same (eg `russiaMilitary` is referred to in Libya and Ukraine reports, but defined first in `russiaConcepts.yaml`) then a second key should not be added as the reference in the linking of the PULSAR-identified perpetrator, victim, or source of information will include the whole namespace. 

Note that if for some reason `russiaMilitary` is not yet a concept in the `RussiaConcepts.yaml` file, then this should be added there (where the groups is most active, present, or located). Then that group can be referred to when connecting the PULSAR mentions/tokens. Concepts should be in the file where they are most important. `BaseConcepts.yaml` should be reserved for non-state and international organizations that do not have an obvious location, where ever possible. Religions that are spread across multiple regions should be in `Base*` also. If a concept is moved from one country file or another or to base, then this should be registered in the `trackingMovementOfConceptsAcrossFiles.yaml` file, see below.

Relations can and must link concepts between `BaseConcepts.yaml` concepts and country-specific concepts, so that there are no isolates in the knowledge graph (eg all `concepts` must be reachable from `ROOT`)


## Tracking movements of concepts to different files

If a concept is moved from one file to another, then this should be registered in the file `trackingMovementOfConceptsAcrossFiles.yaml`

The format should be a sequence that records tuples and in each tuple:

- (from, to, date, mover)

For example 
```
- (UkraineConcepts::wagnerGroupArmedGroup, RussiaConcepts::wagnerGroupArmedGroup, 01/12/23, Colaresi)
- (UnitedKingdomConcepts::AmnestyInternational, BaseConcepts::AmnestyInternational, 04/11/23, Colaresi)
```


## Special characters

No concept names or file names should include double colons ("::") due to their use in defining namespaces 

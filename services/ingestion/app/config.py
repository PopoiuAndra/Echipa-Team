from rdflib import Namespace
import os


FUSEKI_SPARQL_URL = os.getenv(
    "FUSEKI_SPARQL_URL", "http://fuseki:3030/ds/sparql"
)
FUSEKI_UPDATE_URL = os.getenv(
    "FUSEKI_UPDATE_URL", "http://fuseki:3030/ds/update"
)
FUSEKI_DATA_URL = os.getenv(
    "FUSEKI_DATA_URL", "http://fuseki:3030/ds/data"
)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
FUSEKI_ADMIN_PASSWORD = os.getenv("FUSEKI_ADMIN_PASSWORD", "admin")

ENTITIES_GRAPH = "http://example.org/graphs/entities"
ONTOLOGY_GRAPH = "http://example.org/graphs/ontology"

REC = Namespace("http://example.org/rec-onto#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace("https://schema.org/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
WD = Namespace("http://www.wikidata.org/entity/")

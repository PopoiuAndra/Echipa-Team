from __future__ import annotations

import httpx
from rdflib import Graph

from .config import (
    ENTITIES_GRAPH,
    FUSEKI_ADMIN_PASSWORD,
    FUSEKI_DATA_URL,
    FUSEKI_UPDATE_URL,
)


class FusekiClient:
    async def replace_graph(self, graph: Graph) -> int:
        turtle = graph.serialize(format="turtle")
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.put(
                f"{FUSEKI_DATA_URL}?graph={ENTITIES_GRAPH}",
                content=turtle,
                headers={"Content-Type": "text/turtle"},
                auth=("admin", FUSEKI_ADMIN_PASSWORD),
            )
            response.raise_for_status()
        return len(graph)

    async def merge_profile(self, profile_graph: Graph) -> int:
        turtle = profile_graph.serialize(format="turtle")
        sparql_update = (
            "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"
            "PREFIX foaf: <http://xmlns.com/foaf/0.1/>\n"
            "PREFIX schema: <https://schema.org/>\n"
            "PREFIX rec: <http://example.org/rec-onto#>\n"
            "PREFIX wd: <http://www.wikidata.org/entity/> \n"
            "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n"
            "INSERT DATA { GRAPH "
            f"<{ENTITIES_GRAPH}> {{ {turtle_to_sparql_insert(turtle)} }} }}"
        )
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                FUSEKI_UPDATE_URL,
                data={"update": sparql_update},
                headers={"Accept": "application/sparql-results+json"},
                auth=("admin", FUSEKI_ADMIN_PASSWORD),
            )
            response.raise_for_status()
        return len(profile_graph)


def turtle_to_sparql_insert(turtle: str) -> str:
    lines = [
        line
        for line in turtle.splitlines()
        if not line.startswith("@prefix")
    ]
    return "\n".join(lines).strip()

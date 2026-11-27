from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

from .config import ENTITIES_GRAPH, FUSEKI_SPARQL_URL
from .fuseki_client import FusekiClient
from .github_connector import GitHubConnector
from .rdf_mapper import map_profile, safe_id
from .schemas import GithubIngestRequest, IngestResponse, ProfileIngestRequest
from .wikidata_linker import WikidataLinker


app = FastAPI(title="Semantic Knowledge Graph Ingestion API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


LANGUAGE_TO_CONCEPT = {
    "python": "rec:Python",
    "javascript": "rec:JavaScript",
    "typescript": "rec:React",
    "react": "rec:React",
    "java": "rec:BackendTechnologies",
    "go": "rec:BackendTechnologies",
    "rust": "rec:BackendTechnologies",
    "c++": "rec:OpenHardware",
    "c": "rec:OpenHardware",
    "jupyter notebook": "rec:DataScience",
    "r": "rec:DataScience",
}

TOPIC_TO_CONCEPT = {
    "react": "rec:React",
    "javascript": "rec:JavaScript",
    "python": "rec:Python",
    "machine-learning": "rec:MachineLearning",
    "arduino": "rec:Arduino",
    "raspberry-pi": "rec:RaspberryPi",
    "cybersecurity": "rec:Cybersecurity",
    "devops": "rec:DevOps",
    "cloud": "rec:Cloud",
}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest/github", response_model=IngestResponse)
async def ingest_github(request: GithubIngestRequest) -> IngestResponse:
    try:
        profile = await GitHubConnector().fetch_profile(request.github_username)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="GitHub profile request failed") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="GitHub API unavailable") from exc

    skills: dict[str, float] = {}
    for language in profile["languages"]:
        uri = LANGUAGE_TO_CONCEPT.get(language.casefold())
        if uri:
            skills[uri] = max(skills.get(uri, 0.0), 0.85)
    for topic in profile["topics"]:
        uri = TOPIC_TO_CONCEPT.get(topic.casefold())
        if uri:
            skills[uri] = max(skills.get(uri, 0.0), 0.75)

    location_qid = None
    if profile["location"]:
        qid = await WikidataLinker().link(profile["location"])
        if qid:
            location_qid = f"wd:{qid}"

    graph, subject = map_profile(
        request.user_id,
        profile["name"],
        location_qid=location_qid,
        education=profile["bio"],
        occupation=None,
        driving_license=False,
        skills=[{"uri": uri, "proficiency": score} for uri, score in skills.items()],
        preferences=[{"uri": uri} | {"weight": 0.85} for uri in request.extra_preferences],
        aversions=[
            {"uri": uri, "severity": 1.0}
            for uri in request.extra_aversions
        ],
    )
    count = await FusekiClient().merge_profile(graph)
    return IngestResponse(
        user_uri=subject,
        triples_inserted=count,
        extracted_skills=sorted(skills),
    )


@app.post("/ingest/profile", response_model=IngestResponse)
async def ingest_profile(request: ProfileIngestRequest) -> IngestResponse:
    graph, subject = map_profile(
        request.user_id,
        request.name,
        location_qid=request.location_qid,
        education=request.education,
        occupation=request.occupation,
        driving_license=request.driving_license,
        skills=[skill.model_dump() for skill in request.skills],
        preferences=[preference.model_dump() for preference in request.preferences],
        aversions=[aversion.model_dump() for aversion in request.aversions],
    )
    count = await FusekiClient().merge_profile(graph)
    return IngestResponse(user_uri=subject, triples_inserted=count)


@app.get("/graph/{user_id}")
async def get_graph(user_id: str) -> dict:
    subject = f"http://example.org/rec-onto#user_{safe_id(user_id)}"
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX schema: <https://schema.org/>
    PREFIX rec: <http://example.org/rec-onto#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?source ?predicate ?target ?label WHERE {{
      GRAPH <{ENTITIES_GRAPH}> {{
        {{
          <{subject}> ?predicate ?target .
          BIND(<{subject}> AS ?source)
        }}
      }}
      OPTIONAL {{ ?target foaf:name|schema:name|skos:prefLabel ?label }}
    }}
    """
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            response = await client.post(
                FUSEKI_SPARQL_URL,
                data={"query": query},
                headers={"Accept": "application/sparql-results+json"},
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="Fuseki unavailable") from exc

    nodes: dict[str, dict] = {
        subject: {"data": {"id": subject, "label": user_id, "type": "Person"}}
    }
    edges: list[dict] = []
    for row in response.json().get("results", {}).get("bindings", []):
        predicate = row["predicate"]["value"]
        target = row["target"]["value"]
        label = row.get("label", {}).get("value", target.rsplit("#", 1)[-1])
        predicate_name = predicate.rsplit("#", 1)[-1]
        nodes[target] = {
            "data": {
                "id": target,
                "label": label,
                "type": "Concept" if predicate_name in {"hasSkill", "hasPreference", "hasAversion"} else "Attribute",
            }
        }
        edges.append({
            "data": {"source": subject, "target": target, "label": predicate_name}
        })

    return {"nodes": list(nodes.values()), "edges": edges}

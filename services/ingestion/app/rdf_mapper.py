from __future__ import annotations

from rdflib import Graph, Literal, RDF, URIRef, XSD

from .config import FOAF, REC, SCHEMA, WD


def safe_id(value: str) -> str:
    return "".join(ch if ch.isascii() and (ch.isalnum() or ch in "_-") else "_" for ch in value)


def uri_from_contract(value: str) -> URIRef:
    if value.startswith("wd:"):
        return WD[value[3:]]
    if value.startswith("rec:"):
        return REC[value[4:]]
    if value.startswith("http://") or value.startswith("https://"):
        return URIRef(value)
    raise ValueError("URI must use rec:, wd:, http:// or https://")


def map_profile(
    user_id: str,
    name: str,
    *,
    location_qid: str | None = None,
    education: str | None = None,
    occupation: str | None = None,
    driving_license: bool = False,
    skills: list[dict] | None = None,
    preferences: list[dict] | None = None,
    aversions: list[dict] | None = None,
) -> tuple[Graph, str]:
    graph = Graph()
    graph.bind("rec", REC)
    graph.bind("foaf", FOAF)
    graph.bind("schema", SCHEMA)
    graph.bind("wd", WD)

    subject = REC[f"user_{safe_id(user_id)}"]
    graph.add((subject, RDF.type, FOAF.Person))
    graph.add((subject, RDF.type, REC.RecommendableItem))
    graph.add((subject, FOAF.name, Literal(name)))
    graph.add((subject, REC.hasDrivingLicense, Literal(driving_license, datatype=XSD.boolean)))

    if location_qid:
        graph.add((subject, SCHEMA.homeLocation, uri_from_contract(location_qid)))
    if education:
        graph.add((subject, SCHEMA.alumniOf, Literal(education)))
    if occupation:
        graph.add((subject, SCHEMA.hasOccupation, Literal(occupation)))

    for index, skill in enumerate(skills or []):
        node = REC[f"{safe_id(user_id)}_skill_{index}"]
        graph.add((subject, REC.hasSkill, node))
        graph.add((node, RDF.type, REC.WeightedSkill))
        graph.add((node, REC.concept, uri_from_contract(skill["uri"])))
        graph.add((node, REC.proficiency, Literal(skill["proficiency"], datatype=XSD.float)))

    for index, preference in enumerate(preferences or []):
        node = REC[f"{safe_id(user_id)}_preference_{index}"]
        graph.add((subject, REC.hasPreference, node))
        graph.add((node, RDF.type, REC.WeightedPreference))
        graph.add((node, REC.target, uri_from_contract(preference["uri"])))
        graph.add((node, REC.weight, Literal(preference["weight"], datatype=XSD.float)))

    for index, aversion in enumerate(aversions or []):
        node = REC[f"{safe_id(user_id)}_aversion_{index}"]
        graph.add((subject, REC.hasAversion, node))
        graph.add((node, RDF.type, REC.WeightedAversion))
        graph.add((node, REC.target, uri_from_contract(aversion["uri"])))
        graph.add((node, REC.severity, Literal(aversion["severity"], datatype=XSD.float)))

    return graph, str(subject)

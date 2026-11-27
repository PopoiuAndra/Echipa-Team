from __future__ import annotations

from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD


REC = Namespace("http://example.org/rec-onto#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace("https://schema.org/")
WD = Namespace("http://www.wikidata.org/entity/")


def generate_seed_graph(output_path: str | None = None) -> Graph:
    graph = Graph()
    for prefix, namespace in (
        ("rec", REC),
        ("foaf", FOAF),
        ("schema", SCHEMA),
        ("wd", WD),
    ):
        graph.bind(prefix, namespace)

    countries = [WD.Q218, WD.Q843, WD.Q29, WD.Q30, WD.Q183]
    skills = [
        REC.Python,
        REC.React,
        REC.JavaScript,
        REC.MachineLearning,
        REC.Arduino,
        REC.Cloud,
        REC.Cybersecurity,
    ]

    for index in range(12):
        subject = REC[f"user_seed_{index + 1}"]
        graph.add((subject, RDF.type, FOAF.Person))
        graph.add((subject, RDF.type, REC.RecommendableItem))
        graph.add((subject, FOAF.name, Literal(f"Candidate {index + 1}")))
        graph.add((subject, SCHEMA.homeLocation, countries[index % len(countries)]))
        skill = skills[index % len(skills)]
        weighted = REC[f"user_seed_{index + 1}_skill"]
        graph.add((subject, REC.hasSkill, weighted))
        graph.add((weighted, RDF.type, REC.WeightedSkill))
        graph.add((weighted, REC.concept, skill))
        graph.add((weighted, REC.proficiency, Literal(0.65 + (index % 4) * 0.1, datatype=XSD.float)))

        aversion = REC.PhoneCommunication if index % 5 == 0 else REC.Politics
        aversion_node = REC[f"user_seed_{index + 1}_aversion"]
        graph.add((subject, REC.hasAversion, aversion_node))
        graph.add((aversion_node, RDF.type, REC.WeightedAversion))
        graph.add((aversion_node, REC.target, aversion))
        graph.add((aversion_node, REC.severity, Literal(0.85 + (index % 2) * 0.15, datatype=XSD.float)))

    event_names = ["Open Hardware Meetup", "Python Conference", "Horror Film Night", "React Workshop", "Classical Music Festival"]
    for index in range(10):
        subject = REC[f"event_seed_{index + 1}"]
        graph.add((subject, RDF.type, URIRef("https://schema.org/Event")))
        graph.add((subject, RDF.type, REC.RecommendableItem))
        graph.add((subject, SCHEMA.name, Literal(f"{event_names[index % len(event_names)]} {index + 1}")))
        graph.add((subject, SCHEMA.location, countries[index % len(countries)]))
        graph.add((subject, REC.hasTag, skills[index % len(skills)]))

    place_names = ["Innovation Hub", "Library", "Co-working Space", "Music Hall", "Tech Park"]
    for index in range(10):
        subject = REC[f"place_seed_{index + 1}"]
        graph.add((subject, RDF.type, URIRef("https://schema.org/Place")))
        graph.add((subject, RDF.type, REC.RecommendableItem))
        graph.add((subject, SCHEMA.name, Literal(f"{place_names[index % len(place_names)]} {index + 1}")))
        graph.add((subject, SCHEMA.location, countries[index % len(countries)]))
        graph.add((subject, REC.hasTag, skills[index % len(skills)]))

    product_names = ["Free Software Suite", "Arduino Kit", "Cloud Book", "Security Scanner", "ML Course"]
    for index in range(10):
        subject = REC[f"product_seed_{index + 1}"]
        graph.add((subject, RDF.type, URIRef("https://schema.org/Product")))
        graph.add((subject, RDF.type, REC.RecommendableItem))
        graph.add((subject, SCHEMA.name, Literal(f"{product_names[index % len(product_names)]} {index + 1}")))
        graph.add((subject, REC.hasTag, skills[index % len(skills)]))

    service_names = ["Mentoring Service", "DevOps Consulting", "Security Audit", "Data Analysis", "Hardware Prototyping"]
    for index in range(10):
        subject = REC[f"service_seed_{index + 1}"]
        graph.add((subject, RDF.type, URIRef("https://schema.org/Service")))
        graph.add((subject, RDF.type, REC.RecommendableItem))
        graph.add((subject, SCHEMA.name, Literal(f"{service_names[index % len(service_names)]} {index + 1}")))
        graph.add((subject, SCHEMA.location, countries[index % len(countries)]))
        graph.add((subject, REC.hasTag, skills[index % len(skills)]))

    if output_path:
        graph.serialize(destination=output_path, format="turtle")
    return graph


if __name__ == "__main__":
    generate_seed_graph("ontology/seed_data.ttl")

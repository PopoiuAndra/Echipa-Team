# Semantic Knowledge Graph Recommender

Person A implementation for ontology, Fuseki, synthetic seed data, and the ingestion API.

## Run

```bash
cp .env.example .env
docker compose up --build -d
./docker/fuseki/load_seed.sh
```

## Endpoints

- Fuseki: http://localhost:3030/
- Ingestion Swagger: http://localhost:8001/docs

## Person A structure

- `ontology/`: core ontology, SKOS taxonomy, and synthetic RDF data
- `docker/fuseki/`: Fuseki configuration and graph loader
- `services/ingestion/`: GitHub/profile ingestion and Cytoscape graph export

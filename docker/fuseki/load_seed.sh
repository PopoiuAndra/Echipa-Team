#!/usr/bin/env sh
set -eu

FUSEKI_URL="${FUSEKI_URL:-http://localhost:3030}"
DATASET="${FUSEKI_DATASET:-ds}"
ADMIN_PASSWORD="${FUSEKI_ADMIN_PASSWORD:-admin}"

load_graph() {
  file="$1"
  graph="$2"
  curl -fsS -u "admin:${ADMIN_PASSWORD}" \
    -H "Content-Type: text/turtle" \
    --data-binary "@${file}" \
    "${FUSEKI_URL}/${DATASET}/data?graph=${graph}"
}

load_graph "ontology/rec-onto.ttl" "http://example.org/graphs/ontology"
load_graph "ontology/taxonomy.ttl" "http://example.org/graphs/ontology"
load_graph "ontology/seed_data.ttl" "http://example.org/graphs/entities"

printf 'Ontology, taxonomy and seed data loaded into %s/%s\n' "${FUSEKI_URL}" "${DATASET}"

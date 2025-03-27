import numpy as np
import json
import h5py
import sys

file = sys.argv[1]
test = h5py.File(file, "r")["test"]

oes_queries = open("data/opendistroforelasticsearch/queries.txt", "w")
es_queries = open("data/elastic/queries.txt", "w")
vespa_queries = open("data/vespa/queries_ann.txt", "w")

for v in test:
    query_vector = v.tolist()

    # Vespaクエリの生成
    vespa_body = {
        "yql": "select id from doc where {targetHits:10}nearestNeighbor(vector,q)",
        "hits": 10,
        "ranking": "closeness",
        "input.query(q)": query_vector,
    }
    vespa_queries.write("/search/\n")
    vespa_queries.write(json.dumps(vespa_body) + "\n")

    es_body = {
        "size": 10,
        "timeout": "15s",
        "stored_fields": ["_id"],
        "query": {
            "knn": {
                "field": "vector",
                "query_vector": query_vector,
                "k": 10,
            },
        },
    }
    es_queries.write("/doc/_search\n")
    es_queries.write(json.dumps(es_body) + "\n")

    oes_script_query = {"knn": {"vector": {"vector": query_vector, "k": "10"}}}
    oes_body = {
        "size": 10,
        "timeout": "15s",
        "stored_fields": "_none_",
        "docvalue_fields": ["_id"],
        "query": oes_script_query,
    }
    oes_queries.write("/doc/_search\n")
    oes_queries.write(json.dumps(oes_body) + "\n")

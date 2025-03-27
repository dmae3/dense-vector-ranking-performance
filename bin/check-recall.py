import numpy as np
import json
import h5py
import sys
import requests

file = sys.argv[1]
data = h5py.File(file, "r")


def get_vespa_result(query_vector):
    vespa_body = {
        "yql": "select id from doc where {targetHits:10}nearestNeighbor(vector,q)",
        "hits": 10,
        "ranking": "closeness",
        "input.query(q)": query_vector,
    }
    response = requests.post(
        "http://localhost:8090/search/",
        json=vespa_body,
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    hits = []
    for h in response.json()["root"]["children"]:
        id = h["fields"]["id"]
        hits.append(int(id))
    return hits


def get_elastic_result(query_vector):
    es_body = {
        "size": 10,
        "timeout": "15s",
        "stored_fields": ["_id"],
        "query": {"knn": {"field": "vector", "query_vector": query_vector, "k": 10}},
    }
    response = requests.post("http://localhost:9200/doc/_search", json=es_body)
    response.raise_for_status()
    hits = []
    for h in response.json()["hits"]["hits"]:
        id = h["_id"]
        hits.append(int(id))
    return hits


def get_opendistroforelastic_result(query_vector):
    oes_body = {
        "size": 10,
        "timeout": "15s",
        "stored_fields": "_none_",
        "docvalue_fields": ["_id"],
        "query": {"knn": {"vector": {"vector": query_vector, "k": "10"}}},
    }
    response = requests.post("http://localhost:19200/doc/_search", json=oes_body)
    response.raise_for_status()
    hits = []
    for h in response.json()["hits"]["hits"]:
        id = h["fields"]["_id"][0]
        hits.append(int(id))
    return hits


def compute_recall(real_neighbors, computed_neighbors, n=10):
    real_neighbors = real_neighbors[0:n]
    recalled = 0
    for r_n in real_neighbors:
        if r_n in computed_neighbors:
            recalled = recalled + 1
    return recalled / n


average_recall_elastic = []
average_recall_vespa = []
average_recall_opendistroforelastic = []
for i, vector in enumerate(data["test"][0:1000]):
    real_neighbors = data["neighbors"][i]
    distances = data["distances"][i]
    vector = vector.tolist()

    computed_neighbors_oes = get_opendistroforelastic_result(vector)
    computed_neighbors_es = get_elastic_result(vector)
    computed_neighbors_vespa = get_vespa_result(vector)

    recall_opendistroforelastic = compute_recall(real_neighbors, computed_neighbors_oes)
    recall_vespa = compute_recall(real_neighbors, computed_neighbors_vespa)
    recall_elastic = compute_recall(real_neighbors, computed_neighbors_es)
    average_recall_opendistroforelastic.append(recall_opendistroforelastic)
    average_recall_elastic.append(recall_elastic)
    average_recall_vespa.append(recall_vespa)

print("Average recall Vespa = %f" % np.average(average_recall_vespa))
print("Average recall Elastic = %f" % np.average(average_recall_elastic))
print(
    "Average recall Opensearch = %f" % np.average(average_recall_opendistroforelastic)
)

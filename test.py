import h5py
import requests
import json

# MNISTデータの読み込み
file = "mnist-784-euclidean.hdf5"
test = h5py.File(file, "r")["test"]
query_vector = test[0].tolist()  # 最初のベクトルを使用

# Vespaクエリの作成
vespa_body = {
    "yql": "select id from doc where {targetHits:10}nearestNeighbor(vector,q)",
    "hits": 10,
    "ranking": "closeness",
    "input.query(q)": query_vector,
}

# Elasticsearchクエリの作成
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

# OpenSearchクエリの作成
os_body = {
    "size": 10,
    "timeout": "15s",
    "stored_fields": "_none_",
    "docvalue_fields": ["_id"],
    "query": {"knn": {"vector": {"vector": query_vector, "k": "10"}}},
}

# Vespaクエリの実行
print("\nVespa Query:")
response = requests.post(
    "http://localhost:8090/search/",
    json=vespa_body,
    headers={"Content-Type": "application/json"},
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Elasticsearchクエリの実行
print("\nElasticsearch Query:")
response = requests.post(
    "http://localhost:9200/doc/_search",
    json=es_body,
    headers={"Content-Type": "application/json"},
)
print(f"Status: {response.status_code}")
if response.status_code != 200:
    print(f"Error details: {response.text}")
else:
    print(f"Response: {json.dumps(response.json(), indent=2)}")

# OpenSearchクエリの実行
print("\nOpenSearch Query:")
response = requests.post(
    "http://localhost:19200/doc/_search",
    json=os_body,
    headers={"Content-Type": "application/json"},
)
print(f"Status: {response.status_code}")
if response.status_code != 200:
    print(f"Error details: {response.text}")
else:
    print(f"Response: {json.dumps(response.json(), indent=2)}")

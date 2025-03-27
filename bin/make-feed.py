import numpy as np
import json
import h5py
import sys
import gzip
import os
import concurrent.futures
import requests

file = sys.argv[1]
train = h5py.File(file, "r")["train"]


def feed_to_es_and_vespa(data):
    docid, vector = data
    vector = vector.tolist()
    vespa_doc = {"fields": {"id": docid, "vector": vector}}
    es_doc = {"id": docid, "vector": vector}
    try:
        response = requests.post(
            "http://localhost:8090/document/v1/test/doc/docid/%i" % docid,
            json=vespa_doc,
            headers={"Content-Type": "application/json"},
        )
        response = requests.post(
            "http://localhost:9200/doc/_doc/%i" % docid,
            json=es_doc,
            headers={"Content-Type": "application/json"},
        )
        response = requests.post(
            "http://localhost:19200/doc/_doc/%i" % docid,
            json=es_doc,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        print("Error processing document %i: %s" % (docid, str(e)))


ok = 0
failed = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(feed_to_es_and_vespa, data) for data in enumerate(train)]
    for result in concurrent.futures.as_completed(futures):
        try:
            result.result()
            ok += 1
        except:
            failed += 1

print("Feed documents %i - ok %i - failed %i" % (ok + failed, ok, failed))

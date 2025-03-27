#!/bin/sh
docker build . -f Dockerfile.elastic --tag es_benchmark:1.1 --platform linux/arm64 --rm
docker build . -f Dockerfile.opendistroforelasticsearch --tag oes_benchmark:1.1 --platform linux/arm64 --rm
docker build . -f Dockerfile.vespa --tag vespa_benchmark:1.1 --platform linux/arm64 --rm

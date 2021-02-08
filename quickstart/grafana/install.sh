#!/bin/sh

set -e

GRAFANA_NAMESPACE=${GRAFANA_NAMESPACE:-rating}

# shellcheck disable=SC1007
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

kubectl get ns ${GRAFANA_NAMESPACE} >/dev/null 2>&1 || kubectl create ns ${GRAFANA_NAMESPACE}

helm upgrade \
    --install \
    --namespace ${GRAFANA_NAMESPACE} \
    --values "$DIR/values.yaml" \
    grafana \
    grafana/grafana



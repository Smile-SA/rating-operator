#!/bin/bash

set -eu

LOCAL_GRAFANA=${LOCAL_GRAFANA:-false}

[ -z "${RATING_NAMESPACE:-}" ] && echo "RATING_NAMESPACE not set. It is required to install the operator." && exit 1

sed -i "s/namespace: .*/namespace: $RATING_NAMESPACE/" deploy/role_binding.yaml

kubectl create ns "${RATING_NAMESPACE}" || true
kubectl -n ${RATING_NAMESPACE} apply -f deploy/crds/charts.helm.k8s.io_ratings_crd.yaml
kubectl -n ${RATING_NAMESPACE} apply -f deploy/crds/charts.helm.k8s.io_v1alpha1_rating_cr.yaml
kubectl -n ${RATING_NAMESPACE} apply -f deploy/
kubectl -n ${RATING_NAMESPACE} apply -f deploy/v3/ > /dev/null

if [ "$LOCAL_GRAFANA" == "true" ]; then
    GRAFANA_NAMESPACE=${RATING_NAMESPACE} ./quickstart/grafana/install.sh
fi

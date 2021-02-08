#!/bin/sh

GRANAFA_NAMESPACE=${GRANAFA_NAMESPACE:-rating}

helm delete --namespace ${GRANAFA_NAMESPACE} grafana

# kubectl delete -f quickstart/grafana/dashboards/

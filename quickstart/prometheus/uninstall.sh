#!/bin/sh

PROMETHEUS_NAMESPACE=${PROMETHEUS_NAMESPACE:-monitoring}

helm3 delete --namespace ${PROMETHEUS_NAMESPACE} prometheus

# remove the CRDs too
kubectl get crd -o name | grep .monitoring.coreos.com | while read -r resource; do
  kubectl delete "$resource"
done

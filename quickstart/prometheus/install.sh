#!/bin/sh

set -e

PROMETHEUS_NAMESPACE=${PROMETHEUS_NAMESPACE:-monitoring}

# shellcheck disable=SC1007
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

kubectl get ns monitoring >/dev/null 2>&1 || kubectl create ns monitoring

# https://github.com/helm/charts/issues/19452
CREATE_CRDS="--set prometheusOperator.createCustomResource=false"

helm upgrade \
    --install \
    --namespace ${PROMETHEUS_NAMESPACE} \
    --values "$DIR/values.yaml" \
    --version 8.12.3 \
    $HAVE_CRDS \
    --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
    --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false \
    ${CREATE_CRDS} \
    prometheus \
    stable/prometheus-operator

kubectl apply -f dashboards/dashboard.yaml

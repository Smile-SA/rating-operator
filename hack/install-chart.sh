#!/bin/bash

set -eu

[ -z "${RATING_NAMESPACE:-}" ] && echo "RATING_NAMESPACE not set. It is required to install the operator." && exit 1

kubectl create ns "${RATING_NAMESPACE}" || true
helm3 install -n "${RATING_NAMESPACE}" rating ./helm-charts/rating -f values.yaml


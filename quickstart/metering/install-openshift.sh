#!/bin/sh

set -e

die () {
    echo >&2 "$@"
    exit 1
}

# shellcheck disable=SC1007
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

export METERING_NAMESPACE=metering

kubectl create ns ${METERING_NAMESPACE} || true
kubectl -n ${METERING_NAMESPACE} create -f "$DIR/hive-pvc.yaml"

export METERING_CR_FILE="$DIR/metering-custom-openshift.yaml"
"$DIR/operator-metering/hack/openshift-install.sh"

## shellcheck disable=SC2016
"$DIR/retry" --tries=40 --min=10 --max=60 '[ "$(kubectl -n ${METERING_NAMESPACE} get pods -l app=reporting-operator -o jsonpath={.items[*].status.phase})" = "Running" ]' || die 'reporting operator not running'

echo "Installing reports..."
kubectl apply -n ${METERING_NAMESPACE} -Rf "$DIR/manifests/rating"


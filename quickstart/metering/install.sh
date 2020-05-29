#!/bin/sh

set -e

die () {
    echo >&2 "$@"
    exit 1
}

# shellcheck disable=SC1007
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

export METERING_NAMESPACE=${METERING_NAMESPACE:-metering}

export METERING_CR_FILE="$DIR/metering-custom.yaml"
"$DIR/operator-metering/hack/upstream-install.sh"

# shellcheck disable=SC2016
"$DIR/retry" --tries=20 --min=10 --max=60 '[ "$(kubectl -n '${METERING_NAMESPACE}' get pods -l app=reporting-operator -o jsonpath={.items[*].status.phase})" = "Running" ]' || die 'reporting operator not running'

echo "Installing reports..."
kubectl apply -n ${METERING_NAMESPACE} -Rf "$DIR/manifests/rating"


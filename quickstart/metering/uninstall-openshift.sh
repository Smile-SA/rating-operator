#!/bin/sh

set -e

die () {
    echo >&2 "$@"
    exit 1
}

# shellcheck disable=SC1007
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

export METERING_NAMESPACE=metering

echo "Deleting metering reports..."
kubectl -n ${METERING_NAMESPACE} delete reports --all

echo "Deleting hive volume..."
kubectl -n ${METERING_NAMESPACE} delete -f "$DIR/hive-pvc.yaml"

export METERING_CR_FILE="$DIR/metering-custom.yaml"
export SKIP_DELETE_CRDS=false
"$DIR/operator-metering/hack/openshift-uninstall.sh"


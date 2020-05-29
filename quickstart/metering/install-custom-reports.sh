#!/bin/sh

set -e

die () {
    echo >&2 "$@"
    exit 1
}

# shellcheck disable=SC1007
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

export METERING_NAMESPACE=metering

for metric in cpu-request cpu-usage memory-request memory-usage; do
  kubectl create -n ${METERING_NAMESPACE} -Rf "$DIR/manifests/rating/$metric/ReportQuery"
  kubectl create -n ${METERING_NAMESPACE} -Rf "$DIR/manifests/rating/$metric/ReportDataSource"
  kubectl create -n ${METERING_NAMESPACE} -Rf "$DIR/manifests/rating/$metric/Report"
done


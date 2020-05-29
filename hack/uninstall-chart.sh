#!/bin/bash

set -eu

[ -z "${RATING_NAMESPACE:-}" ] && echo "RATING_NAMESPACE not set. It is required to install the operator." && exit 1

helm3 -n "${RATING_NAMESPACE}" delete rating


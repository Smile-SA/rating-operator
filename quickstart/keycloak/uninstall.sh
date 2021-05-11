#!/bin/sh

set -e

KEYCLOAK_NAMESPACE=${KEYCLOAK_NAMESPACE:-keycloak}

DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

kubectl -n ${KEYCLOAK_NAMESPACE} delete -Rf "$DIR/keycloak.yaml"

kubectl delete namespaces keycloak 




#!/bin/sh

set -e

KEYCLOAK_NAMESPACE=${KEYCLOAK_NAMESPACE:-keycloak}

DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

kubectl get ns ${KEYCLOAK_NAMESPACE} >/dev/null 2>&1 || kubectl create ns ${KEYCLOAK_NAMESPACE}

kubectl apply -n ${KEYCLOAK_NAMESPACE} -Rf "$DIR/keycloak.yaml"



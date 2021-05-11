#!/bin/sh

set -e

OPENLDAP_NAMESPACE=${OPENLDAP_NAMESPACE:-openldap}

DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

kubectl get ns ${OPENLDAP_NAMESPACE} >/dev/null 2>&1 || kubectl create ns ${OPENLDAP_NAMESPACE}

helm upgrade \
    --install \
    --namespace ${OPENLDAP_NAMESPACE} \
    --values "$DIR/values.yaml" \
    openldap \
    helm-openldap/openldap 

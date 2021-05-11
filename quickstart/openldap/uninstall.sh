#!/bin/sh

set -e

OPENLDAP_NAMESPACE=${OPENLDAP_NAMESPACE:-openldap}

helm delete --namespace ${OPENLDAP_NAMESPACE} openldap 

kubectl delete namespaces openldap

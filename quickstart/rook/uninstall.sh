#!/bin/sh

set -e

die () {
    echo >&2 "$@"
    exit 1
}

ROOK_NAMESPACE=${ROOK_NAMESPACE:-rook-ceph}

# shellcheck disable=SC1007
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

MANIFESTS_DIR="$DIR/rook/cluster/examples/kubernetes/"

echo 'Removing cephblockpool: replicapool...'
kubectl -n ${ROOK_NAMESPACE} get cephblockpool replicapool >/dev/null 2>&1 && kubectl -n ${ROOK_NAMESPACE} delete cephblockpool replicapool

echo 'Removing storageclass: rook-ceph-block...'
kubectl get storageclass rook-ceph-block >/dev/null 2>&1 && kubectl delete storageclass rook-ceph-block

echo 'Removing storageclass: csi-cephfs...'
kubectl get storageclass csi-cephfs >/dev/null 2>&1 && kubectl delete storageclass csi-cephfs

echo "Removing cephcluster: rook-ceph"
kubectl -n ${ROOK_NAMESPACE} get cephcluster rook-ceph >/dev/null 2>&1 && kubectl -n ${ROOK_NAMESPACE} delete cephcluster rook-ceph

sleep 10

[ "$(kubectl -n ${ROOK_NAMESPACE} get cephcluster --no-headers 2>/dev/null)" = "" ] || die 'Ceph cluster was not removed'

echo "Removing Helm release: rating"
helm delete --namespace ${ROOK_NAMESPACE} rook

# echo "Removing deployments, daemonsets..."
# kubectl -n ${ROOK_NAMESPACE} delete daemonset --all
# kubectl -n ${ROOK_NAMESPACE} delete deployment --all
#
# echo "Removing services..."
# kubectl -n ${ROOK_NAMESPACE} delete service --all

# kubectl delete -f "$MANIFESTS_DIR/ceph/common.yaml"


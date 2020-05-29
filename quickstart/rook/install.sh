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

echo "Installing Helm release..."
kubectl get ns rook-ceph >/dev/null 2>&1 || kubectl create ns rook-ceph
helm3 upgrade --install rook "$DIR/rook/cluster/charts/rook-ceph" --namespace ${ROOK_NAMESPACE} --set image.tag=v1.2.6

sleep 30

echo "Creating cluster..."
kubectl apply -f "$MANIFESTS_DIR/ceph/cluster-test.yaml"
echo "Creating block storage class..."
kubectl apply -f "$MANIFESTS_DIR/ceph/csi/rbd/storageclass-test.yaml"

# You can set the storageclass as default, so that it will be used when the application manifests specify "null".

kubectl patch storageclass rook-ceph-block -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

echo "Waiting for cluster creation..."
# shellcheck disable=SC2016
"$DIR/retry" --tries=20 --min=10 --max=60 '[ "$(kubectl -n '${ROOK_NAMESPACE}' get cephcluster rook-ceph -o jsonpath='"'"'{.status.state}'"'"')" = "Created" ]' || die 'Ceph cluster not created yet'

echo "Creating shared filesystem..."
kubectl apply -f "$MANIFESTS_DIR/ceph/filesystem-test.yaml"
echo "Creating fs storage class..."
kubectl apply -f "$MANIFESTS_DIR/ceph/csi/cephfs/storageclass.yaml"


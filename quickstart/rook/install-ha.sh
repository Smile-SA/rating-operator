#!/bin/sh

set -e

die () {
    echo >&2 "$@"
    exit 1
}

# shellcheck disable=SC1007
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

MANIFESTS_DIR="$DIR/rook/cluster/examples/kubernetes/"

echo "Installing Helm release..."
helm install --name rook --namespace rook-ceph --set image.tag=v1.1.2 "$DIR/rook/cluster/charts/rook-ceph"

sleep 30

echo "Creating cluster..."
kubectl create -f "$MANIFESTS_DIR/ceph/cluster.yaml"
echo "Creating block storage class..."
kubectl create -f "$MANIFESTS_DIR/ceph/csi/rbd/storageclass.yaml"

# You can set the storageclass as default, so that it will be used when the application manifests specify "null".

kubectl patch storageclass rook-ceph-block -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

echo "Waiting for cluster creation..."
# shellcheck disable=SC2016
"$DIR/retry" --tries=20 --min=10 --max=60 '[ "$(kubectl -n rook-ceph get cephcluster rook-ceph -o jsonpath='"'"'{.status.state}'"'"')" = "Created" ]' || die 'Ceph cluster not created yet'

echo "Creating shared filesystem..."
kubectl create -f "$MANIFESTS_DIR/ceph/filesystem.yaml"
echo "Creating fs storage class..."
kubectl create -f "$MANIFESTS_DIR/ceph/csi/cephfs/storageclass.yaml"


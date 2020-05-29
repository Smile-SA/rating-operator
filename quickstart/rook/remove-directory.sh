#!/bin/sh

set -e

CLUSTER_DOMAIN="my.domain.here"

echo "Removing /var/lib/rook on each node..."
for node in $(kubectl get nodes -o name | cut -d / -f2); do
    ssh "$node.${CLUSTER_DOMAIN}" 'sudo rm -rf /var/lib/rook/'
done


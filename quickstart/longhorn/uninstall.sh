# Remove the RWX provider and storage class
kubectl delete -f ./quickstart/longhorn/longhorn/examples/rwx/01-security.yaml
kubectl delete -f ./quickstart/longhorn/longhorn/examples/rwx/02-longhorn-nfs-provisioner.yaml

# Uninstall the Helm release
helm uninstall longhorn
# Install the longhorn ecosystem
kubectl create namespace longhorn-system
helm install longhorn ./quickstart/longhorn/longhorn/chart/ --namespace longhorn-system

# Install the RWX storage-class and provider
# https://longhorn.io/docs/1.0.1/advanced-resources/rwx-workloads/
kubectl apply -f ./quickstart/longhorn/longhorn/examples/rwx/01-security.yaml
kubectl apply -f ./quickstart/longhorn/longhorn/examples/rwx/02-longhorn-nfs-provisioner.yaml

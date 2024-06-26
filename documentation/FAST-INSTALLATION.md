# **Installation**

## 1. Introduction

In this document we show how to set up a test/minimal cluster instance. In a production
environment, you may want to add Network policies for increased security, and
HA storage for resilience. In this tutorial the in-cluster communications are
considered trusted.

## 2. Requirements

- A Kubernetes cluster (tested on 1.14 through 1.17) or OpenShift 4.x, configured to be accessible from the local machine.
- Helm 3
- 'Rating Operator' project cloned to local machine
- A storage provider (By default Longhorn, rook-ceph available)
- A Prometheus instance configured to collect from kubelet and kube-state-metrics.
   In OpenShift, you can use the provided monitoring stack (the `openshift-monitoring` project).
- Users authentication (optional)

### 2.1. Kubernetes

Note that as of today, our strategy is not to support both OKD and Kubernetes, but rather focus over Kubernetes in the future versions of Rating Operator. 


For **local installation**, a light weight cluster can be installed locally using k3s, make sure the local machine has a minimum storage of 20GB.

If not installing locally, please proceed to Helm installation:

```sh
$ curl -sfL https://get.k3s.io | sh -
```

A kubernetes config file is required, if using a remote cluster - it can be found on the master node, in case of local cluster it can be found at ```/etc/rancher/k3s/k3s.yaml```.

```sh
$ sudo chmod +r /etc/rancher/k3s/k3s.yaml
$ export KUBECONFIG=/etc/rancher/k3s/k3s.yaml 
```
Check if kubectl is working fine:
```sh
$ kubectl get namespaces
```
This should return default kubernetes namespaces  

Local installtion also requires open-iscsi: 
```sh
$ sudo apt install open-iscsi
```


Once we have a local/remote kubernetes cluster, we can proceed with Helm installation.


### 2.2. Helm 3

Helm 3 does away with some security issues of its previous versions (no server-side Tiller component), but you may want to restrict Helm's permissions in a production environment. To know more, see [Securing Helm 3 - Matthew Fisher, Microsoft](https://static.sched.com/hosted_files/helmsummit2019/08/Securing%20Helm%203%20-%20Helm%20Summit%20EU%202019.pptx).
To prevent compatibility problems, we recommend using version 3.1.2 of helm.

```sh
$ curl https://get.helm.sh/helm-v3.1.2-linux-amd64.tar.gz | tar xfz -
$ sudo mv linux-amd64/helm /usr/local/bin/helm
```

### 2.3. Cloning project

Before proceeding, please clone the project repository and `cd` into it:

```sh
$ git clone https://github.com/Smile-SA/rating-operator.git
```

### 2.4. Storage provider

Two solutions are available for storage, each one having advantages and uses-cases.

**Longhorn** is lighter, more adapted to smaller scale. On the other hand, **Rook/ceph** is heavier but easily scalable.
You can also install both to try it out.

**Longhorn** is recommanded for standard installation.

Once the storage provider is installed, if you do not intend on testing both, we recommand skipping to the next step.

To modify the provider storageClass, follow the instructions in [configuration](/documentation/CONFIGURE.md).

#### 2.4.1. Longhorn

To install Longhorn, go through the following steps:

First, clone the repository to your machine:

```sh
$ git clone https://github.com/longhorn/longhorn ./quickstart/longhorn/longhorn
```
We will get the following output:
```
Cloning into './longhorn/longhorn'...
remote: Enumerating objects: 1, done.
[...]
```

Then, apply the manifest to install it:

```sh
$ kubectl apply -f ./quickstart/longhorn/longhorn/deploy/longhorn.yaml
```
We will get the following output:
```sh
[...]
namespace/longhorn-system configured
serviceaccount/longhorn-service-account configured
clusterrole.rbac.authorization.k8s.io/longhorn-role configured
clusterrolebinding.rbac.authorization.k8s.io/longhorn-bind configured
customresourcedefinition.apiextensions.k8s.io/engines.longhorn.io configured
customresourcedefinition.apiextensions.k8s.io/replicas.longhorn.io configured
customresourcedefinition.apiextensions.k8s.io/settings.longhorn.io configured
customresourcedefinition.apiextensions.k8s.io/volumes.longhorn.io configured
customresourcedefinition.apiextensions.k8s.io/engineimages.longhorn.io configured
customresourcedefinition.apiextensions.k8s.io/nodes.longhorn.io configured
customresourcedefinition.apiextensions.k8s.io/instancemanagers.longhorn.io configured
customresourcedefinition.apiextensions.k8s.io/sharemanagers.longhorn.io configured
configmap/longhorn-default-setting configured
podsecuritypolicy.policy/longhorn-psp configured
role.rbac.authorization.k8s.io/longhorn-psp-role configured
rolebinding.rbac.authorization.k8s.io/longhorn-psp-binding configured
configmap/longhorn-storageclass configured
daemonset.apps/longhorn-manager configured
service/longhorn-backend configured
deployment.apps/longhorn-ui configured
service/longhorn-frontend configured
deployment.apps/longhorn-driver-deployer **configured**

```



Wait a minute, then verify everything is working as expected by running:

```sh
$ kubectl get pods -n longhorn-system
```
We will get the following output:
```sh
NAME                                        READY   STATUS    RESTARTS   AGE
csi-attacher-7965bb8b59-cjgz5               1/1     Running   0          1m4s
csi-attacher-7965bb8b59-gtq8b               1/1     Running   0          1m4s
csi-attacher-7965bb8b59-hn678               1/1     Running   0          1m4s
csi-provisioner-5896666d9b-992s8            1/1     Running   0          1m4s
csi-provisioner-5896666d9b-fsdpq            1/1     Running   0          1m4s
csi-provisioner-5896666d9b-xl2g8            1/1     Running   0          1m4s
csi-resizer-98674fffd-2v7vr                 1/1     Running   0          1m4s
csi-resizer-98674fffd-nd4tl                 1/1     Running   0          1m4s
csi-resizer-98674fffd-pk7jk                 1/1     Running   0          1m4s
engine-image-ei-ee18f965-hhrfz              1/1     Running   0          1m4s
engine-image-ei-ee18f965-mngvz              1/1     Running   0          1m4s
engine-image-ei-ee18f965-vlrsn              1/1     Running   0          1m4s
instance-manager-e-20fff56d                 1/1     Running   0          1m4s
instance-manager-e-c1848f67                 1/1     Running   0          1m4s
instance-manager-e-e664f00d                 1/1     Running   0          1m4s
instance-manager-r-4a9375cd                 1/1     Running   0          1m4s
instance-manager-r-a39e4e14                 1/1     Running   0          1m4s
instance-manager-r-d931b401                 1/1     Running   0          1m4s
longhorn-csi-plugin-2rhz8                   2/2     Running   0          1m4s
longhorn-csi-plugin-6qckv                   2/2     Running   0          1m4s
longhorn-csi-plugin-q79k6                   2/2     Running   0          1m4s
longhorn-driver-deployer-6f675d86d4-xq85n   1/1     Running   0          1m4s
longhorn-manager-6vnsv                      1/1     Running   0          1m4s
longhorn-manager-89rb7                      1/1     Running   1          1m4s
longhorn-manager-f8ntf                      1/1     Running   0          1m4s
longhorn-nfs-provisioner-67ddb7ffc9-qzlft   1/1     Running   0          1m4s
longhorn-ui-6c5b56bb9c-x6ldw                1/1     Running   0          1m4s
```

### 2.5. Prometheus
#### 2.5.1. Installation
**DISCLAIMER** Be sure to take a look at the Prometheus `./quickstart/prometheus/values.yaml` file before proceeding with the installation.

For more informations, please read the [configuration documentation](/documentation/CONFIGURE.md).

We will use the chart of the prometheus-community repository for this example:

**https://github.com/prometheus-community/helm-charts**

```sh
$ helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
```
We will get the following output:
```sh
"prometheus-community" has been added to your repositories
```

Once added to your helm repository, update it to be sure to have the latest version

```sh
$ helm repo update
```
After updating successfully:
```sh
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "prometheus-community" chart repository
Update Complete. ⎈ Happy Helming!⎈
```

You can also find Prometheus already installed in your K8s/Openshift distribution.
The important things for each method are the connection and authentication details.

When the helm repository is updated, deploy the Prometheus Operator with:

```sh
$ ./quickstart/prometheus/install.sh
```

Information shown as:
```sh
NAME:   prometheus
LAST DEPLOYED: Thu Oct 10 16:17:01 2019
NAMESPACE: monitoring
STATUS: DEPLOYED
[...]
```

Wait a minute, then verify everything is working as expected by running:
```sh
$ kubectl get pods -n monitoring
```
After running, we will get the following output:
```sh
NAME                                                     READY   STATUS    RESTARTS   AGE
prometheus-kube-prometheus-operator-9f9748b4-pzs94       1/1     Running   0          48s
prometheus-prometheus-node-exporter-dlfjq                1/1     Running   0          48s
prometheus-kube-state-metrics-6ccff77dbb-6k4xc           1/1     Running   0          48s
alertmanager-prometheus-kube-prometheus-alertmanager-0   2/2     Running   0          44s
prometheus-prometheus-kube-prometheus-prometheus-0       2/2     Running   0          44s
prometheus-grafana-5845df476-nnvq8                       3/3     Running   0          48s

```


## 3. Rating Operator

### 3.1. Installation
There's two installation method for the rating-operator:

- As an operator
- As an Helm chart
  
We recommend deploying the operator version.
Use the chart only if you want full control over updates, configuration and CustomResources.

Before installing the operator, please consider reading [this document](/documentation/CONFIGURE.md), as the default configuration that comes included in the rating-operator might not suit your case.

#### 3.1.1. Installing as an operator

Make sure that all pods are running in ```monitoring``` namespace before proceeding
Choose a namespace and deploy the operator in it.

```sh
$ RATING_NAMESPACE=rating hack/install.sh
```
By running the above command, we will get the following output:
```sh
customresourcedefinition.apiextensions.k8s.io/ratings.charts.helm.k8s.io created
rating.charts.helm.k8s.io/rating created
deployment.apps/rating-operator created
clusterrole.rbac.authorization.k8s.io/rating-operator created
clusterrolebinding.rbac.authorization.k8s.io/rating-operator created
serviceaccount/rating-operator created
```

Beware: the installation script modifies in place the file deploy/role_bindings.yaml, so be careful not to commit its changes back to the repository.


To check if everything is running correctly:

```sh
$ kubectl -n rating get pods
```
We will get the following output:
```sh
NAME                                        READY   STATUS    RESTARTS   AGE
rating-operator-755d6bdbd9-27vcj            1/1     Running   0          45s
rating-operator-api-66c9484866-rvdjj        1/1     Running   0          45s
rating-operator-postgresql-0                1/1     Running   0          45s
rating-operator-manager-bdf55cd99-k4ffs     1/1     Running   0          45s
rating-operator-engine-5bc9948b88-lt49q     1/1     Running   0          45s
```

### 3.2. Accessing rating operator  

While inside the rating operator repo, and inside the rating namespace, run:

```sh
$ sudo kubectl config set-context --current --namespace=rating
```

Then we can access rating operator components:

**Rating-api**
```sh
$ ./hack/forward-api
```

**Prometheus**
```sh
$ ./hack/forward-prometheus
```

**Grafana**
```sh
$ ./hack/forward-grafana
```
## 4. Uninstallation

### 4.1. Rating Operator

```sh
RATING_NAMESPACE=rating ./hack/uninstall.sh
```

or if you installed with Helm:

```sh
$ RATING_NAMESPACE=rating ./hack/uninstall-chart.sh
```

### 4.2. Longhorn

To remove Longhorn, run:
- First, to run the uninstaller

```sh
$ kubectl apply -f ./quickstart/longhorn/longhorn/uninstall/uninstall.yaml
```
- Then:
```sh
$ kubectl delete -f /quickstart/longhorn/longhorn/deploy/longhorn.yaml
```
- Finally:
```sh
$ kubectl delete -f /quickstart/longhorn/longhorn/uninstall/uninstall.yaml
```

### 4.4. Prometheus

Helm does not remove CRD objects, hence the need of a script to do so.

```sh
$ ./quickstart/prometheus/uninstall.sh
```
The above command will produce the output as follows:

```sh
release "prometheus" deleted
customresourcedefinition.apiextensions.k8s.io "alertmanagers.monitoring.coreos.com" deleted
[...]
customresourcedefinition.apiextensions.k8s.io "prometheusrules.monitoring.coreos.com" deleted
customresourcedefinition.apiextensions.k8s.io "servicemonitors.monitoring.coreos.com" deleted
```

### 4.5. Grafana

If you installed Grafana manually, run:

```sh
$ GRAFANA_NAMESPACE=rating ./quickstart/grafana/uninstall.sh
```



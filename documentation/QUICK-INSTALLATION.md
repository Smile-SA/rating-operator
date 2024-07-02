# **Installation**

## 1. Introduction

In this document we show how to set up a test/minimal cluster instance. In a production
environment, you may want to add Network policies for increased security, and
HA storage for resilience. In this tutorial the in-cluster communications are
considered trusted.

## 2. Requirements

### 2.1. Kubernetes




For **local installation**, a light weight cluster can be installed locally using k3s, make sure the local machine has a minimum storage of 20GB.



```sh
 curl -sfL https://get.k3s.io | sh -
```



```sh
 sudo chmod +r /etc/rancher/k3s/k3s.yaml
 export KUBECONFIG=/etc/rancher/k3s/k3s.yaml 
```
Check if kubectl is working fine:
```sh
 kubectl get namespaces
```
This should return default kubernetes namespaces  

Local installtion also requires open-iscsi: 
```sh
 sudo apt install open-iscsi
```


Once we have a local/remote kubernetes cluster, we can proceed with Helm installation.


### 2.2. Helm 3



```sh
 curl https://get.helm.sh/helm-v3.1.2-linux-amd64.tar.gz | tar xfz -
 sudo mv linux-amd64/helm /usr/local/bin/helm
```

### 2.3. Cloning project

Before proceeding, please clone the project repository and `cd` into it:

```sh
 git clone https://github.com/Smile-SA/rating-operator.git
```

### 2.4. Storage provider



**Longhorn** is recommanded for standard installation.


#### 2.4.1. Longhorn

To install Longhorn, go through the following steps:

First, clone the repository to your machine:

```sh
 git clone https://github.com/longhorn/longhorn ./quickstart/longhorn/longhorn
```


Then, apply the manifest to install it:

```sh
 kubectl apply -f ./quickstart/longhorn/longhorn/deploy/longhorn.yaml
```




Wait a minute, then verify everything is working as expected by running:

```sh
 kubectl get pods -n longhorn-system
```

### 2.5. Prometheus
#### 2.5.1. Installation
**DISCLAIMER** Be sure to take a look at the Prometheus `./quickstart/prometheus/values.yaml` file before proceeding with the installation.

For more informations, please read the [configuration documentation](/documentation/CONFIGURE.md).

We will use the chart of the prometheus-community repository for this example:

**https://github.com/prometheus-community/helm-charts**

```sh
 helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
```

Once added to your helm repository, update it to be sure to have the latest version

```sh
 helm repo update
```

When the helm repository is updated, deploy the Prometheus Operator with:

```sh
 ./quickstart/prometheus/install.sh
```


Wait a minute, then verify everything is working as expected by running:
```sh
 kubectl get pods -n monitoring
```

## 3. Rating Operator

### 3.1. Installation

#### 3.1.1. Installing as an operator

Make sure that all pods are running in ```monitoring``` namespace before proceeding
Choose a namespace and deploy the operator in it.

```sh
 RATING_NAMESPACE=rating hack/install.sh
```

Beware: the installation script modifies in place the file deploy/role_bindings.yaml, so be careful not to commit its changes back to the repository.


To check if everything is running correctly:

```sh
 kubectl -n rating get pods
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
 sudo kubectl config set-context --current --namespace=rating
```

Then we can access rating operator components:

**Rating-api**
```sh
 ./hack/forward-api
```

**Prometheus**
```sh
 ./hack/forward-prometheus
```

**Grafana**
```sh
 ./hack/forward-grafana
```
## 4. Uninstallation

### 4.1. Rating Operator

```sh
RATING_NAMESPACE=rating ./hack/uninstall.sh
```

### 4.2. Longhorn

To remove Longhorn, run:
- First, to run the uninstaller

```sh
 kubectl apply -f ./quickstart/longhorn/longhorn/uninstall/uninstall.yaml
```
- Then:
```sh
 kubectl delete -f /quickstart/longhorn/longhorn/deploy/longhorn.yaml
```
- Finally:
```sh
 kubectl delete -f /quickstart/longhorn/longhorn/uninstall/uninstall.yaml
```

### 4.4. Prometheus



```sh
 ./quickstart/prometheus/uninstall.sh
```

### 4.5. Grafana



```sh
 GRAFANA_NAMESPACE=rating ./quickstart/grafana/uninstall.sh
```



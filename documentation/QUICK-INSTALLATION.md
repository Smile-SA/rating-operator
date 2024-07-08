# **Installation**

## 1. Introduction

In this document we show how to set up a test/minimal cluster instance.
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


Local installtion also requires open-iscsi: 
```sh
 sudo apt install open-iscsi
```





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
| **Endpoint**            | Description                                                           | Parameters                                      |
|-------------------|-----------------------------------------------------------------------|-----------------------------------------------------|
| **GET `/instances/list`**           | Get the list of the rating rules instances from the local configuration directory.        | No parameters expected. |
|  **GET `/instances/get`**             | Get the rating rule instance object for a given instance name                            |Expect a payload with : `name`  |
| **POST `/instances/add`**        | Add and deploy the rating rule instance.| Expect a payload with : `metric_name`  `template_name` and variables values|
| **POST `/instances/edit`**  | edit the rating rule instance.            | Expect a payload with : `metric_name`  `template_name` and variables values |
| **POST `/instances/delete`** | Delete a rating rule instance.              | Expect a payload with : `metric_name` |
| **GET `/templates/list`**           | Get the list of all the RatingRules templates names from the local configuration directory.        | No parameters expected. |
|  **GET `/templates/get`**             | Get the RatingRule template object for a given template.                          |Expect a payload with : `query_name`  |
| **POST `/templates/add`**        | Add a new RatingRule template. | Expect a payload with : `query_name`  `query_group` and `query_template`|
| **POST `/templates/edit`**  | Edit a template configuration.            | Expect a payload with : `query_name`  `query_group` and `query_template` |
| **POST `/templates/delete`** | Delete a template configuration.| Expect a payload with : `query_name` |
| **GET `/metrics`**           | Get the list of metrics.| No parameters expected. |
| **GET `/metrics/<metric_name>/rating`**           | Get the rating for a given metric.| Parameters expected : `start`  `end` |
| **GET `/metrics/<metric_name>/total_rating`**           | Get the aggragated rating for a given metric. | Parameters expected : `start`  `end` |
| **GET `/metrics/<metric>/<aggregator>`**           | Get the rating for a given metric, according to the aggregator. | Available aggregator are: `daily`  `weekly` `monthly` |
| **GET `/metrics/<metric>/todate`**           | Get the rating, from the start of the month to now. | No parameters expected. |

for more details about the API, please consult [API endpoints](/documentation/API.md)


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
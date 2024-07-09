## **Installation**

In this document we show how to set up a test/minimal cluster instance. For more details, please refer to the full **[Installation](/documentation/INSTALL.md).**

### 1. Kubernetes

Install a light weight cluster by k3s (minimum 20GB of storage).

```sh
 curl -sfL https://get.k3s.io | sh -
```



```sh
 sudo chmod +r /etc/rancher/k3s/k3s.yaml
 export KUBECONFIG=/etc/rancher/k3s/k3s.yaml 
```

```sh
 sudo apt install open-iscsi
```





### 2. Helm 3



```sh
 curl https://get.helm.sh/helm-v3.1.2-linux-amd64.tar.gz | tar xfz -
 sudo mv linux-amd64/helm /usr/local/bin/helm
```

### 3. Cloning project

Clone the project repository and `cd` into it:

```sh
 git clone https://github.com/Smile-SA/rating-operator.git
```

### 4. Storage provider





Install Longhorn


```sh 
git clone https://github.com/longhorn/longhorn ./quickstart/longhorn/longhorn

kubectl apply -f ./quickstart/longhorn/longhorn/deploy/longhorn.yaml
```





Wait a minute, then verify everything is working as expected by running:

```sh
 kubectl get pods -n longhorn-system
```

### 5. Prometheus

```sh
 helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

 helm repo update

./quickstart/prometheus/install.sh
```
Wait a minute, then verify everything is working as expected by running:
```sh
 kubectl get pods -n monitoring
```

### 6. Rating Operator

#### 6.1 Installing as an operator

```sh
 RATING_NAMESPACE=rating hack/install.sh
```

To check if everything is running correctly:

```sh
 kubectl -n rating get pods
```
#### 6.2. Accessing rating operator  

While inside the rating operator repo, and inside the rating namespace, run:

```sh
 sudo kubectl config set-context --current --namespace=rating
```

Then we can access rating operator components:

**Rating-api**
```sh
 ./hack/forward-api
```
for more details about the API, please consult [API endpoints](/documentation/API.md)

**Prometheus**
```sh
 ./hack/forward-prometheus
```

**Grafana**
```sh
 ./hack/forward-grafana
```

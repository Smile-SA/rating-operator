# **Installation**

## Introduction

In this document we show how to set up a test/minimal instance. In a production
environment, you may want to add Network policies for increased security, and
HA storage for resilience. In this tutorial the in-cluster communications are
considered trusted.

## Requirements

- A Kubernetes cluster (tested on 1.14 through 1.17) or OpenShift 4.x9
- A storage provider (By default Longhorn, rook-ceph available)
- Helm is used to deploy Prometheus, or the storage if you need to.
- A Prometheus instance configured to collect from kubelet and kube-state-metrics.
   We will show you how to deploy one (currently with no authentication).
   In OpenShift, you can use the provided monitoring stack (the `openshift-monitoring` project).


### *Helm*

Helm 3 does away with some security issues of its previous versions (no server-side Tiller component), but you may want to restrict Helm's permissions in a production environment. To know more, see [Securing Helm 3 - Matthew Fisher, Microsoft](https://static.sched.com/hosted_files/helmsummit2019/08/Securing%20Helm%203%20-%20Helm%20Summit%20EU%202019.pptx).
To prevent compatibility problems, we recommend using version 3.1.2 of helm.
```sh
$ curl https://get.helm.sh/helm-v3.1.2-linux-amd64.tar.gz | tar xfz -
$ sudo mv linux-amd64/helm /usr/local/bin/helm
```

### Storage provider

Two solutions are available for storage, each one having advantages and uses-cases.

**Longhorn** is lighter, more adapted to smaller scale. On the other hand, **Rook/ceph** is heavier but easily scalable.
You can also install both to try it out.

**Longhorn** is recommanded for standard installation.

Once you have your storage provider installed, please skip the other as having both will not bring any benefits.

To modify the provider storageClass, follow the instructions in [configuration](/documentation/CONFIGURATION.md).
#### *Longhorn*

To install Longhorn, go through the following steps:

First, clone the repository to your machine:

```sh
$ git clone https://github.com/longhorn/longhorn ./quickstart/longhorn/longhorn
Cloning into './longhorn/longhorn'...
remote: Enumerating objects: 1, done.
[...]
```

Then, apply the manifest to install it:

```sh
$ kubectl apply -f ./quickstart/longhorn/longhorn/deploy/longhorn.yaml
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

To test the volumes provisionning, run:
`./quickstart/longhorn/longhorn/examples/simple_pvc.yaml`

Then, confirm with
```sh
$ kubectl get pvc -n longhorn-system
NAME                       STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
longhorn-simple-pvc        Bound    pvc-432e9316-6fbc-4bcb-8e7a-b7eb97011826   1Gi        RWO            longhorn       10s
```

#### *Rook-Ceph*

From [helm-operator documentation](https://github.com/rook/rook/blob/master/Documentation/helm-operator.md):

```sh
$ git clone https://github.com/rook/rook.git -b v1.2.6 ./quickstart/rook/rook
Cloning into './rook/rook'...
remote: Enumerating objects: 75, done.
[...]
$ ./quickstart/rook/install.sh
Installing Helm release...
NAME:   rook
[...]
Creating fs storage class...
storageclass.storage.k8s.io/csi-cephfs created
```

The above installs the helm chart and creates a few objects (CephCluster, StorageClass, CephFilsystem...).

NOTE: The default setup and the rest of the document describe a minimal test
cluster, where the node hosting the volumes is a single point of failure. In
production you will want to use a robust configuration, by changing the
`rook/install.sh` script. The Rook repository comes with [several examples](https://github.com/rook/rook/blob/master/Documentation/ceph-examples.md) that you can choose and adapt to your desired setup: development, production, HA or not, error correction, performance and retention policies,
etc. You can define multiple CephClusters, but they need to be installed in
separate namespaces.

When everything is running correcly, with two worker nodes you should see something like:

```sh
$ kubectl get pods -n rook-ceph
NAME                                  READY   STATUS    RESTARTS   AGE
rook-ceph-agent-g48jg                 1/1     Running   0          100s
rook-ceph-agent-mm9vx                 1/1     Running   0          100s
rook-ceph-operator-6c8b6f68c5-6ddxh   1/1     Running   3          2m39s
rook-discover-2zf8p                   1/1     Running   0          100s
rook-discover-zh7jz                   1/1     Running   0          100s
```

You can now test the dynamic volumes:

```yml
$ cat <<EOT | kubectl create -f -
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pv-claim
spec:
  storageClassName: rook-ceph-block
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi
EOT
persistentvolumeclaim/test-pv-claim created
```


After a few seconds, you should see a new Persistent Volume, to which the pvc is bound:

```sh
$ kubectl get pv,pvc
NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                                                                                                                       STORAGECLASS             REASON   AGE
persistentvolume/pvc-15e45593-ad59-11e9-855f-52540001fa54   2Gi        RWO            Delete           Bound    marco/test-pv-claim                                                                                                         rook-ceph-block                   2m

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS      AGE
persistentvolumeclaim/test-pv-claim   Bound    pvc-15e45593-ad59-11e9-855f-52540001fa54   2Gi        RWO            rook-ceph-block   2m5s
```


### *Prometheus*

Be sure to take a look at the Prometheus `values.yaml` file before proceeding with the installation.

We will use the chart of the prometheus-community repository for this example:

**https://github.com/prometheus-community/helm-charts**

```sh
$ helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
"prometheus-community" has been added to your repositories
```

Once added to your helm repository, update it to be sure to have the latest version

```sh
$ helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "prometheus-community" chart repository
Update Complete. ⎈ Happy Helming!⎈
```

You can also find Prometheus already installed in your K8s/Openshift distribution.
The important things for each method are the connection and authentication details.

When the helm repository is updated, deploy the Prometheus Operator with:

```sh
$ ./quickstart/prometheus/install.sh

NAME:   prometheus
LAST DEPLOYED: Thu Oct 10 16:17:01 2019
NAMESPACE: monitoring
STATUS: DEPLOYED
[...]
```

Data persistence is off by default, but can be enabled in <https://github.com/helm/charts/blob/master/stable/prometheus-operator/values.yaml[values.yaml>],
for prometheus and/or the alertmanager:

```yml
[...]
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: rook-ceph-block # Or longhorn
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 50Gi
        selector: {}
[...]
```

NOTE: If Prometheus is using Ceph volumes, it can't effectively alert you on the
availability of the storage. When Ceph goes down, so does Prometheus.

After the above installation, the prometheus URL inside the cluster should be
`http://prometheus-prometheus-oper-prometheus.monitoring:9090/`, without
authentication.

#### Grafana

##### Standard

**prometheus-operator** deploys its own **Grafana** instance.
Through the `quickstart/prometheus/values.yaml`, we provide a base Grafana configuration that includes:

- plugins to query `rating-operator` data
- datasource for `rating-operator`
- Three dashboards, including rated data:
  - IAAS costs simulation
  - Application specifics
  - Rating-operator resources consumption

In order to edit the dashboards, you either need to edit:
  - The ConfigMap
  - The file (`./quickstart/prometheus/dashboards`), then apply with `kubectl -f`.

##### Non-standard

If, for any reason, you cannot access or modify the main Grafana instance of your cluster, we provide a script to install Grafana with the rating-operator.
Don't forget to update the `deploy/operator.yaml` with the adress of your Grafana instance.
More infos in the [configuration documentation](/documentation/CONFIGURATION.md).

### *Metering Operator* (Optional, skip if your use case is not LARGE scale)

**DISCLAIMER**: The metering-operator project is not maintained anymore. We consider the metering based rating to be deprecated.
**DISCLAIMER**: The `metering-operator` is only required  for the *scalable* rating, as it uses the operator's `Reports` objects. If you only need a *light* solution to rate dataframes, skip this step.

#### Operator configuration

Check the metering configuration file. Do not apply it with kubectl, since the corresponding CRD does not exist yet.

NOTE: You need to change the prometheus URL with your own if you installed it with another method.


```sh
$ cat ./metering/metering-custom.yaml
[...]
  storage:
    type: "hive"
    hive:
      type: "sharedPVC"
      sharedPVC:
        createPVC: true
        storageClass: "csi-cephfs"
        size: 5Gi
```


#### Installing the operator

Clone the repository, then run the install script:

```sh
$ git clone https://github.com/operator-framework/operator-metering.git -b release-4.2 ./quickstart/metering/operator-metering
Cloning into 'operator-metering'...
[...]

$ ./quickstart/metering/install.sh
[...]
Creating namespace metering
namespace/metering created
Installing Custom Resource Definitions
customresourcedefinition.apiextensions.k8s.io/hivetables.metering.openshift.io created
customresourcedefinition.apiextensions.k8s.io/reportdatasources.metering.openshift.io created
[...]
meteringconfig.metering.openshift.io/operator-metering created
Before retry #1: sleeping 10 seconds
Before retry #2: sleeping 20 seconds
Before retry #3: sleeping 40 seconds
Before retry #4: sleeping 60 seconds
Before retry #5: sleeping 60 seconds
Installing reports...
[...]
report.metering.openshift.io/pod-cpu-request-hourly created
report.metering.openshift.io/pod-cpu-usage-hourly created
report.metering.openshift.io/pod-memory-request-hourly created
report.metering.openshift.io/pod-memory-usage-hourly created
```

You can check that the operator is running correctly with:

```sh
$ kubectl -n metering get pods
NAME                                  READY   STATUS    RESTARTS   AGE
hive-metastore-0                      1/1     Running   0          14m
hive-server-0                         1/1     Running   0          14m
metering-operator-6c746c5cb6-tnbq7    2/2     Running   0          18m
presto-coordinator-0                  1/1     Running   0          13m
reporting-operator-56c49bcc4b-zwhd9   1/1     Running   1          12m
```


The running status of the reports should slowly transition from InvalidReport to ReportingPeriodWaiting:

```sh
$ kubectl get report -n metering
NAME                                QUERY                        SCHEDULE   RUNNING                  FAILED   LAST REPORT TIME   AGE
cluster-cpu-capacity-daily          cluster-cpu-capacity         daily      ReportingPeriodWaiting                               3m53s
cluster-cpu-capacity-hourly         cluster-cpu-capacity         hourly     ReportingPeriodWaiting                               3m53s
cluster-cpu-usage-daily             cluster-cpu-usage            daily      ReportingPeriodWaiting                               3m53s
cluster-cpu-usage-hourly            cluster-cpu-usage            hourly     ReportingPeriodWaiting                               3m53s
[...]
```

**DISCLAIMER**: Please wait for the first `Reports` to be generated before proceeding with the next step, at it may cause hazards. More info in [this document](/documentation/TROUBLESHOOT.md)

### *Rating*

There's two installation method for the rating-operator:
-  As an operator
-  As an Helm chart
  
We recommend deploying the operator version.
Use the chart only if you want full control over updates, configuration and CustomResources.

Before installing the operator, please consider reading [this document](/documentation/TROUBLESHOOT.md), as the default configuration that comes included in the rating-operator might not suit your case.
#### Installing the operator


Choose a namespace and deploy the operator in it.

```sh
$ RATING_NAMESPACE=rating hack/install.sh
customresourcedefinition.apiextensions.k8s.io/ratings.charts.helm.k8s.io created
rating.charts.helm.k8s.io/rating created
deployment.apps/rating-operator created
clusterrole.rbac.authorization.k8s.io/rating-operator created
clusterrolebinding.rbac.authorization.k8s.io/rating-operator created
serviceaccount/rating-operator created
```

Beware: the installation script modifies in place the file deploy/role_bindings.yaml, so be careful not to commit its changes back to the repository.

#### Installing the Helm chart

Call Helm to install the charts in the namespace of your choice:

```
$ helm install -n rating rating ./helm-charts/rating -f ./values.yaml
NAME: rating
LAST DEPLOYED: Wed Apr  8 14:42:54 2020
NAMESPACE: rating-mm
STATUS: deployed
[...]
```

The arguments are: namespace, name of the release, directory of the chart.


To check if everything is running correctly:

```sh
$ kubectl -n rating get pods
NAME                                READY   STATUS    RESTARTS   AGE
rating-api-66c9484866-rvdjj         1/1     Running   0          45s
rating-operator-755d6bdbd9-27vcj    1/1     Running   0          45s
rating-postgresql-0                 1/1     Running   0          45s
rating-processing-bdf55cd99-k4ffs   1/1     Running   0          45s
rating-reactive-5bc9948b88-lt49q    1/1     Running   0          45s
```

## Uninstall

### Rating

```sh
$ RATING_NAMESPACE=rating ./hack/uninstall.sh
```

or if you installed with Helm:

```sh
$ RATING_NAMESPACE=rating ./hack/uninstall-chart.sh
```


### Metering operator and configuration

```sh
$ ./metering/uninstall.sh
Deleting metering reports...
report.metering.openshift.io "cluster-cpu-capacity-daily" deleted
report.metering.openshift.io "cluster-cpu-capacity-hourly" deleted
[...]
customresourcedefinition.apiextensions.k8s.io "prestotables.metering.openshift.io" deleted
customresourcedefinition.apiextensions.k8s.io "reports.metering.openshift.io" deleted
Deleting PVCs
No resources found
```


### Rook-Ceph

Removing the rook-ceph chart does not remove the pods nor the /var/lib/rook
directory on each of the nodes. To completely remove the rook-ceph components:

```sh
$ ./quickstart/rook/uninstall.sh
Removing cephblockpool: replicapool...
cephblockpool.ceph.rook.io "replicapool" deleted
Removing storageclass: rook-ceph-block...
storageclass.storage.k8s.io "rook-ceph-block" deleted
[...]
Removing services...
service "csi-cephfsplugin-metrics" deleted
service "csi-rbdplugin-metrics" deleted
$ ./rook/remove-directory.sh
Removing /var/lib/rook on each node...
```

Adapt these scripts to your environment, especially `remove-directory.sh` which
needs to connect with ssh to each worker node.


### Prometheus

Helm does not remove CRD objects, hence the need of a script to do so.

```sh
$ ./quickstart/prometheus/uninstall.sh
release "prometheus" deleted
customresourcedefinition.apiextensions.k8s.io "alertmanagers.monitoring.coreos.com" deleted
[...]
customresourcedefinition.apiextensions.k8s.io "prometheusrules.monitoring.coreos.com" deleted
customresourcedefinition.apiextensions.k8s.io "servicemonitors.monitoring.coreos.com" deleted
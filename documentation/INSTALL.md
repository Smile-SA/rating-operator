# **Installation**

## Introduction

In this document we show how to set up a test/minimal instance. In a production
environment, you may want to add Network policies for increased security, and
HA storage for resilience. In this tutorial the in-cluster communications are
considered trusted.

## Requirements

- A Kubernetes cluster (tested on 1.14 through 1.17) or OpenShift 4.x9
- A persistent storage plugin that supports the ReadWriteMany access mode, i.e. a shared
   filesystem that can be written from multiple nodes simultaneously. We describe how to
   install https://rook.io/[Rook] and https://ceph.com/[Ceph] to that purpose.
   Some distributions, like CodeReady, come with pre-provisioned volumes
   without the need to install anything else. NFS is not recommended.
- Helm is used to deploy Prometheus, or the Rook storage if you need to.
- A Prometheus instance configured to collect from kubelet and kube-state-metrics.
   We will show you how to deploy one (currently with no authentication).
   In OpenShift, you can use the provided monitoring stack (the `openshift-monitoring` project).
- https://github.com/jzelinskie/faq (on the machine that is running kubectl)


### *Helm*

Helm 3 does away with some security issues of its previous versions (no server-side Tiller component), but you may want to restrict Helm's permissions in a production environment. To know more, see [Securing Helm 3 - Matthew Fisher, Microsoft](https://static.sched.com/hosted_files/helmsummit2019/08/Securing%20Helm%203%20-%20Helm%20Summit%20EU%202019.pptx).
To prevent compatibility problems, we recommand using version 3.1.2 of helm.
```sh
$ curl https://get.helm.sh/helm-v3.1.2-linux-amd64.tar.gz | tar xfz -
$ sudo mv linux-amd64/helm /usr/local/bin/helm3
```

### Storage provider

Two solutions are available for storage, each one having advantages and uses-cases.
**Longhorn** is lighter, more adapted to smaller scale. On the other hand, **Rook/ceph** is heavier but easily scalable.
You can also install both to try it out.

To change the method of provisionning volumes, replace the storageClass variable in further configurations.
**Longhorn** is enabled by default.

#### *Longhorn*


```sh
$ git clone https://github.com/longhorn/longhorn ./quickstart/longhorn/longhorn
Cloning into './longhorn/longhorn'...
remote: Enumerating objects: 1, done.
[...]
```

Once the repository is cloned, please edit
`./quickstart/longhorn/longhorn/examples/rwx/02-longhorn-nfs-provisioner.yaml`
as follows:

```
line 18:   clusterIP: 10.43.111.111 
```

Replace this by a valid IP in the range `10.152.183.0/24`.
Once this is done, proceed to the installation.

```sh
$ ./quickstart/longhorn/install.sh
namespace/longhorn-system created
NAME: longhorn
[...]
Longhorn is now installed on the cluster!
Please wait a few minutes for other Longhorn components such as CSI deployments, Engine Images, and Instance Managers to be initialized.
[...]
persistentvolumeclaim/longhorn-nfs-provisioner created
storageclass.storage.k8s.io/longhorn-nfs created
[...]
```

If you modified the file correctly, everything should be initializating / running.
To confirm, use:
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

To test the RWX volumes, run:
`./quickstart/longhorn/longhorn/examples/rwx/03-rwx-test.yaml`

To test the RWO volumes, run:
`./quickstart/longhorn/longhorn/examples/simple_pvc.yaml`

Then, confirm with
```sh
$ kubectl get pvc -n longhorn-system
NAME                       STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
longhorn-nfs-provisioner   Bound    pvc-a9413e35-86af-4779-a557-35ca02ed0722   19Gi       RWO            longhorn       2m3s
longhorn-simple-pvc        Bound    pvc-432e9316-6fbc-4bcb-8e7a-b7eb97011826   1Gi        RWO            longhorn       10s
nfs-test                   Bound    pvc-d7b37379-d4b9-4dc7-ae42-d45be11e79ba   1Gi        RWX            longhorn-nfs   3s
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

```
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

You can install Prometheus in a multitude of ways, including:

- https://github.com/helm/charts/tree/master/stable/prometheus-operator
- https://github.com/helm/charts/tree/master/stable/prometheus
- https://github.com/coreos/kube-prometheus

You can also find Prometheus already installed in your k8s/openshift distribution.

The important things for each method are the connection and authentication details.

To deploy the Prometheus Operator with the right configuration:

```sh
$ ./quickstart/prometheus/install.sh

NAME:   prometheus
LAST DEPLOYED: Thu Oct 10 16:17:01 2019
NAMESPACE: monitoring
STATUS: DEPLOYED
[...]
```

Data persistence is off by default, but can be enabled in https://github.com/helm/charts/blob/master/stable/prometheus-operator/values.yaml[values.yaml],
for prometheus and/or the alertmanager:

```
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
availability of the storage. When Ceph goes down, so does Prometheus. For rating
purposes, you don't actually need persistence of Prometheus data, since the metrics
to be rated are shipped to the metering component for long-term storage as soon
as possible.

After the above installation, the prometheus URL inside the cluster is
`http://prometheus-prometheus-oper-prometheus.monitoring:9090/`, without
authentication.

#### Grafana

By default, **prometheus-operator** installs it's own **Grafana** instance in its namespace.
We provide a base Grafana configuration that includes:

- plugins to query `rating-operator` data
- datasource for `rating-operator`
- simple dashboard

To modify the dashboard, you need to modify its ConfigMap, named `grafana-dashboards-configmap`.
We provide an example dashboard file at `./quickstart/prometheus/dashboards/dashboard.yaml`.


### *Metering Operator*

**DISCLAIMER**: The `metering-operator` is only required  for the *scalable* rating, as it uses the operator's `Reports` objects. If you only need a *light* solution to rate dataframes, skip this step.

#### Operator configuration

Check the metering configuration file. Do not apply it with kubectl, since the corresponding CRD does not exist yet.

NOTE: You need to change the prometheus URL with your own if you installed it with another method.


```sh
$ cat ./metering/metering-custom-longhorn.yaml
[...]
  storage:
    type: "hive"
    hive:
      type: "sharedPVC"
      sharedPVC:
        createPVC: true
        storageClass: "longhorn-nfs"
        size: 5Gi
```


#### Installing the operator

Install [faq (Format Agnostic jQ)](https://github.com/jzelinskie/faq) on the machine where you are running kubectl.

Clone the repository, then run the install script:

```sh
$ git clone https://github.com/operator-framework/operator-metering.git -b release-4.2 ./quickstart/metering/operator-metering
Cloning into 'operator-metering'...
[...]
$ ./quickstart/metering/install.sh
Using /home/marco/5g/valentin/rating-setup/metering/operator-metering/manifests/deploy/upstream/metering-ansible-operator as manifests directory
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

You can install the rating stack in two ways: as an operator, or via the Helm chart.

You also have to set a password for Postgres. If you don't, it will be randomly generated
by helm each time you install or update the chart, but the new password will not be set
in the database's volume, and the server will refuse all connections ( https://github.com/helm/charts/issues/362 ).


#### Installing the operator

Choose a namespace and deploy the operator on it.

You can set the Postgres password in `deploy/operator.yaml`


```sh
$ RATING_NAMESPACE=rating hack/install.sh
customresourcedefinition.apiextensions.k8s.io/ratings.charts.helm.k8s.io created
rating.charts.helm.k8s.io/rating created
deployment.apps/rating-operator created
clusterrole.rbac.authorization.k8s.io/rating-operator created
clusterrolebinding.rbac.authorization.k8s.io/rating-operator created
serviceaccount/rating-operator created
```

Beware: the install script modifies in place the file deploy/role_bindings.yaml, so be careful not to commit its changes back to the repository.

#### Installing the Helm chart

To deploy the rating services as a Helm release, create a `values.yaml` file
with at least the Postgres password:

```
postgresql:
  postgresqlPassword: <PASSWORD HERE>
```

Then call Helm to install the charts in the namespace of your choice:

```
$ helm3 install -n rating rating ./helm-charts/rating -f ./values.yaml
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

Helm does not remove CRD objects so we'll do it in a script.

```sh
$ ./quickstart/prometheus/uninstall.sh
release "prometheus" deleted
customresourcedefinition.apiextensions.k8s.io "alertmanagers.monitoring.coreos.com" deleted
[...]
customresourcedefinition.apiextensions.k8s.io "prometheusrules.monitoring.coreos.com" deleted
customresourcedefinition.apiextensions.k8s.io "servicemonitors.monitoring.coreos.com" deleted
```


# **Custom Resources**

The `rating-operator` uses *CustomResources* for most of its configuration need.
It also emits one to notify other applications of the availability of data.
We describe in this document every aspect of each resources we use, with usable examples.

## ***ratings**.charts.helm.k8s.io*

This resource describes a rating instance, and is used by the operator to deploy the needed stack.
It holds application specific parameters, such as image versions, resource limitations, or Prometheus instance location.
An example of such object can be found [here](/deploy/crds/charts.helm.k8s.io_v1alpha1_rating_cr.yaml) and is documented in [there](/documentation/CONFIGURE.md).

The operator watch this resource and react to change to adapt the instance accordingly.
Multiple `Rating` stacks can be deployed in the same cluster, but only one rating instance is allowed per namespace.
The operator can, from its namespace, handle multiple `Rating` objects, and deploy them in their respective location.

You can experiment with your `Rating` configuration by running:

```sh
$ kubectl edit ratings.charts.helm.k8s.io rating
# Do some changes, changing port numbers for example
[...]
rating.charts.helm.k8s.io/rating edited
```

Once the changes are accepted, you will see the operator reconfiguring the rating stack with the new parameters.

## ***ratingrules**.rating.alterway.fr*

 [This description is applicable from Rating operator v2.0]

To create rules, we define two custom resources `RatingRuleTemplate` and `RatingRuleInstance`:

-  `RatingRuleTemplate`: describes the `promql query` with a list of variables
-  `RatingRuleInstance`: describes the `Metric` with a given values for the variables decribed in the associated `RatingRuleTemplate promql query` 

Each `RatingRuleInstance` is created from a `RatingRuleTemplate` with specific `RatingRuleValues` that are stored in the postgres database.

Consider this minimal example of a `RatingRuleTemplate` that calculates the cloud resources cost:

```yml
---
apiVersion: rating.alterway.fr/v1
kind: RatingRuleTemplate
metadata: 
    name: rating-rule-template-cloud-cost
    namespace: rating
spec: 
    query_name : cloud-cost
    query_group : cost-simulation
    query_template : ((ceil(sum(instance:node_memory_utilisation:ratio) * max(node_memory_MemTotal_bytes)/(1024*1024*1024)))/{memory} > (ceil(sum(instance:node_cpu:ratio) * max(instance:node_num_cpu:sum)))/{cpu} or (ceil(sum(instance:node_cpu:ratio) * max(instance:node_num_cpu:sum)))/{cpu}) * {price}             
    
```
Each `RatingRuleTemplate` has a name (i.e. `query_name`), a goup (i.e. `query_group`)  that contains a number of `RatingRuleTemplates` and the quey.
In this `RatingRuleTemplate`, the described `query_template` has three variables: `cpu`, `memory` and `price`.

A `RatingRuleInstance` is an instance of a template with specific values. To create an instance, you should specify the `metric_name`, `templae_name` and provide the values for the query variables. For example, for the **cloud-cost** `RatingRuleTemplate` defined above, if we provide to the API/instances/add the following`RatingRuleValues`:


```yml
---
- metric_name: aws-cost
- template_name: cloud-cost
- cpu: 1
- memory: 1
- price: 0.5
- timeframe: 3600s

```

Or `kubectl apply -f instance.yaml` :

```yml
---
apiVersion: rating.alterway.fr/v1
kind: RatingRuleInstance
metadata:
  name: rating-rule-instance-aks-cost
  namespace: rating
spec:
  metric: ((ceil(sum(instance:node_memory_utilisation:ratio) * max(node_memory_MemTotal_bytes)/(1024*1024*1024)))/{memory} > (ceil(sum(instance:node_cpu:ratio) * max(instance:node_num_cpu:sum))) / {cpu} or (ceil(sum(instance:node_cpu:ratio) * max(instance:node_num_cpu:sum)))/{cpu}) * {price}
  name: aks-cost
  timeframe: 3600s
  cpu: "1"
  memory: "1"
  price: "0.5"

```


The resulted `RatingRuleInstance` will be:

```yml
---
apiVersion: rating.alterway.fr/v1
kind: RatingRuleInstance
metadata:
  creationTimestamp: "2021-08-19T23:06:12Z"
  name: rating-rule-instance-aws-cost
  namespace: rating
  ownerReferences:
  - apiVersion: charts.helm.k8s.io/v1alpha1
    blockOwnerDeletion: true
    controller: true
    kind: Rating
    name: rating
    uid: 5e8bf7fd-04dc-4786-8745-f2e690c1029a
  resourceVersion: "74473530"
  selfLink: /apis/rating.alterway.fr/v1/namespaces/rating/ratingruleinstances/rating-rule-instance-node-cost-simulation-aks-a8
  uid: 887ae58c-025e-41c6-8761-ad47960d36ce
spec:
  cpu: "1"
  memory: "1"
  metric: ((ceil(sum(instance:node_memory_utilisation:ratio) * max(node_memory_MemTotal_bytes)/(1024*1024*1024)))/{memory}
    > (ceil(sum(instance:node_cpu:ratio) * max(instance:node_num_cpu:sum))) / {cpu}
    or (ceil(sum(instance:node_cpu:ratio) * max(instance:node_num_cpu:sum)))/{cpu})
    * {price}
  name: aks-cost
  price: "0.5"
  timeframe: 3600s

```

----

Three keys have to be defined in a `RatingRuleInstance`:

- **metric** defines what to query from Prometheus. Every valid PromQL expression can be used here.
- **name** is the name of the metric
- **timeframe** correspond to the time between every data processing run. It also defines the precision of your metric. Only values in seconds are accepted, as shown above. In case of wrong format, base value is used (60s)

As soon as this resource is created, the rating will pick it up and start processing frames.

**Hint** Before lowering the **timeframe** parameter too much, make sure your storage capatibilities can handle it (Depending of the metric, it can produce big storage imprint quite quickly). There's no mechanism yet to rotate the data in the database, and multiple, low timeframes `RatingRuleInstances` can generate lots of data.

It is also possible to use `PrometheusRules` to let Prometheus pre-process your customized metrics, and only let the rating query it.
Consider this example:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  labels:
    app: prometheus-operator
    role: alert-rules
  name: prometheus-rating.rules
  namespace: monitoring
spec:
  groups:
  - name: rating.rules
    rules:
    - expr: (sum(rate(container_memory_usage_bytes[1h])) BY (pod, namespace) + on
        (pod, namespace) group_left(node) (sum(kube_pod_info{pod_ip!="",node!="",host_ip!=""})
        by (pod, namespace, node) * 0)) * on () group_left() usage_memory
      record: rating:pod_memory_usage:unlabeled
```

The `expr` key is the PromQL expression, and the metric become available to be queried as `record`, here `rating:pod_memory_usage:unlabeled`.
This resource is better described in their [documentation](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/).


The most recent `RatingRuleInstance` is exposed to Prometheus, making all the values and labelset available for query building with promQL (in RatedMetrics, for example)
You can expect to find each **labelSet** with their respective value plus the value of default ruleset as metric in Prometheus.
```sh
usage_cpu{[...]}
usage_cpu{[...], foo="bar"}
```

To get a list of the metrics exposed to Prometheus, query the `/rules_metrics` endpoint of the **rating-operator-api**.

```sh
$ curl http://rating-operator-api.rating:80/rules_metrics
request_cpu 1
usage_cpu 1
request_memory 1
usage_memory 1
# EOF
```




## *ratedmetrics.rating.alterway.fr*

Everytime a rated frames is written to the database, a `RatedMetric` is emitted.
It contains informations about the metric, for other operators or applications to bind onto:

```yaml
apiVersion: rating.alterway.fr/v1
kind: RatedMetric
metadata:
  name: rated-test-metric
  namespace: rating
spec:
  date: "2020-07-30T13:39:42Z"
  metric: test_metric
```

It only contains two keys:

- **date** represent the time of the last data write
- **metric** defines the metric to query from the API

Watching updates of this custom resource helps only querying new data from our system.
Creation of a `RatedMetric` has to be done by the rating-operator, not the user.

It is possible to delete a `RatedMetric` to trigger the reprocessing of the given metric.
In case of changes applied to an older set of rules, this is how one should act. More information on why [here](/documentation/FEATURES.md).

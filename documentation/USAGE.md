# **Usage**

## Configuring

Within the `rating-operator` deployment is included a base configuration, a **RatingRule**.

#### RatingRules

```sh
$ kubectl get ratingrules.rating.smile.fr
NAME                          AGE
rating-default-rules          46m

$ kubectl describe ratingrules.rating.smile.fr rating-rating-default-rules
[...]
Spec:
# The "Metrics" part describe the location of the metric in the metering-operator
# This part is about to be removed, as the metering-operator is now deprecated.
  Metrics:
    request_cpu:
      presto_column:  pod_request_cpu_core_seconds
      presto_table:   report_metering_pod_rating_cpu_request_hourly
      report_name:    pod-rating-cpu-request-hourly
      Unit:           core-seconds
    request_memory:
      presto_column:  pod_request_memory_byte_seconds
      presto_table:   report_metering_pod_rating_memory_request_hourly
      report_name:    pod-rating-memory-request-hourly
      Unit:           byte-seconds
    usage_cpu:
      presto_column:  pod_usage_cpu_core_seconds
      presto_table:   report_metering_pod_rating_cpu_usage_hourly
      report_name:    pod-rating-cpu-usage-hourly
      Unit:           core-seconds
    usage_memory:
      presto_column:  pod_usage_memory_byte_seconds
      presto_table:   report_metering_pod_rating_memory_usage_hourly
      report_name:    pod-rating-memory-usage-hourly
      Unit:           byte-seconds


# The "Rules" part holds the value with which to multiply metrics
  Rules:
    Name:  rules_default
    Ruleset:
      Metric:  request_cpu
      Value:   0.5
      Unit:    core-hours
      Metric:  usage_cpu
      Value:   0.8
      Unit:    core-hours
      Metric:  request_memory
      Value:   0.4
      Unit:    GiB-hours
      Metric:  usage_memory
      Value:   0.8
      Unit:    GiB-hours
[...]
```

This configuration will be used until a new one is created.
You can edit the above with:

```sh
$ kubectl edit ratingrules.rating.smile.fr <yourconfig>
```

For more advanced use cases, we strongly advice to create a new configuration.
The rating-operator does not allow modification on the base configuration, and it is provided to help the application run as default.

**DISCLAIMER** The part below describe features that are only compatible with the *metering-operator* based rating, which is deprecated.
The RatingRules also provide assistance through metrics declarations and configuration versionning for the *metering-operator* version.
To understand why, read the *configuration versionning* part of [this document](/documentation/FEATURES.md) document.

More information on `RatingRules` can be found in the [custom resources documentation](/documentation/CRD.md).

#### RatedRules

The other part of the configuration is composed of **RatingRuleInstances**, describing metrics using **promQL** and of a base **RatingRule** that holds values to be used in queries.

```sh
$ kubectl get ratingruleinstances.rating.smile.fr
NAME                                                           AGE
rating-rule-instance-pod-request-cpu                              2m
rating-rule-instance-pod-request-memory                           2m
rating-rule-instance-pod-usage-cpu                                2m
rating-rule-instance-pod-usage-memory                             2m

$ kubectl get ratingruleinstances.rating.smile.fr rating-rule-instance-pod-usage-cpu -o yaml
kind: RatingRuleInstance
metadata:
  name: rating-rule-instance-pod-usage-cpu
spec:
  metric: usage_cpu * on() group_right sum(rate(container_cpu_usage_seconds_total[1m]))
    BY (pod, namespace) + on (pod, namespace) group_left(node) (sum(kube_pod_info{pod_ip!="",node!="",host_ip!=""})
    by (pod, namespace, node) * 0)
  name: pods_usage_cpu
  timeframe: 60s
```

More informations on `RatingRuleInstances` can be found in the [custom resources documentation](/documentation/CRD.md).

----

## Adding new metrics

To rate a new metric, you need to create a `RatingRuleInstance`:

```sh
$ kubectl get ratingRuleInstances.rating.smile.fr                             
NAME                            AGE
rating-rule-instance-rated-usage-cpu   21s

$ kubectl describe ratingRuleInstances.rating.smile.fr rating-rule-instance-rated-usage-cpu
Name:         rating-rule-instance-rated-usage-cpu
Namespace:    rating
Labels:       <none>
Annotations:  <none>
API Version:  rating.smile.fr/v1
Kind:         RatingRuleinstance
[...]
Spec:
  # Metric have to be a valid prometheus query
  # In this example, we are using the value of "usage_memory" described in the RatingRules above to rate our frames
  Metric: -|
    (sum(rate(container_memory_usage_bytes[1h])) BY (pod, namespace) + on (pod, namespace) group_left(node) (sum(kube_pod_info{pod_ip!="",node!="",host_ip!=""}) by (pod, namespace, node) * 0)) * on () group_left() usage_memory

  # This is the name of the metric once rated
  Name:       test_metric

  # Only second is supported
  Timeframe:  10s
[...]
```
As soon as the `RatingRuleInstances` is validated, the `rating-operator-engine` will start processing frames.
More information on `RatingRuleInstances` can be found in the [custom resources documentation](/documentation/CRD.md).


## Templates and instances historization

In Rating operator, we keep a history of the templates and instances modification in the Postgres database.


1. Templates historization:

| id                         | template_name | template_group | template_var     | template_query |
|----------------------------|---------------|----------------|------------------|----------------|
| 2021-10-26 10:28:27.266831 | name          | gname          | cpu-memory-price | ceil(ceil...   |

2. Instances historization:

| start_time                 | end_time                   | instance_name                          | instance_promql | instance_values                                   |
|----------------------------|----------------------------|----------------------------------------|-----------------|---------------------------------------------------|
| 2021-10-26 10:25:53.735273 | 2021-10-26 10:25:54.193911 | umber_instance_simulation_aws_a1_large | ceil(ceil...    | {'cpu': '2', 'price': '0.05<br>1', 'memory': '4'} |
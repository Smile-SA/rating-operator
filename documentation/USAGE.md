# **Usage**

## Configuring

Within the `rating-operator` deployment is included a base configuration, a **RatingRule**.

#### RatingRules

```sh
$ kubectl get ratingrules.rating.alterway.fr
NAME                          AGE
rating-default-rules          46m

$ kubectl describe ratingrules.rating.alterway.fr rating-rating-default-rules
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
$ kubectl edit ratingrules.rating.alterway.fr <yourconfig>
```

For more advanced use cases, we strongly advice to create a new configuration.
The rating-operator does not allow modification on the base configuration, and it is provided to help the application run as default.

**DISCLAIMER** The part below describe features that are only compatible with the *metering-operator* based rating, which is deprecated.
The RatingRules also provide assistance through metrics declarations and configuration versionning for the *metering-operator* version.
To understand why, read the *configuration versionning* part of [this document](/documentation/FEATURES.md) document.

More information on `RatingRules` can be found in the [custom resources documentation](/documentation/CRD.md).

#### RatedRules

The other part of the configuration is composed of **ReactiveRules**, describing metrics using **promQL** and of a base **RatingRule** that holds values to be used in queries.

```sh
$ kubectl get reactiverules.rating.alterway.fr
NAME                                                       AGE
reactive-rule-pod-request-cpu                              2m
reactive-rule-pod-request-memory                           2m
reactive-rule-pod-usage-cpu                                2m
reactive-rule-pod-usage-memory                             2m

$ kubectl get reactiverules.rating.alterway.fr reactive-rule-pod-usage-cpu -o yaml
kind: ReactiveRule
metadata:
  name: reactive-rule-pod-usage-cpu
spec:
  metric: usage_cpu * on() group_right sum(rate(container_cpu_usage_seconds_total[1m]))
    BY (pod, namespace) + on (pod, namespace) group_left(node) (sum(kube_pod_info{pod_ip!="",node!="",host_ip!=""})
    by (pod, namespace, node) * 0)
  name: pods_usage_cpu
  timeframe: 60s
```

More informations on `ReactiveRules` can be found in the [custom resources documentation](/documentation/CRD.md).
----

## Adding new metrics

To rate a new metric, you need to create a `ReactiveRule`:

```sh
$ kubectl get reactiverules.rating.alterway.fr                             
NAME                            AGE
reactive-rule-rated-usage-cpu   21s

$ kubectl describe reactiverules.rating.alterway.fr reactive-rule-rated-usage-cpu
Name:         reactive-rule-rated-usage-cpu
Namespace:    rating
Labels:       <none>
Annotations:  <none>
API Version:  rating.alterway.fr/v1
Kind:         ReactiveRule
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

Every variable present in the **LATEST** RatingRule will be available through Prometheus, and usable in ReactiveRules.

As soon as the `ReactiveRules` is validated, the `rating-operator-engine` will start processing frames.
More information on `ReactiveRules` can be found in the [custom resources documentation](/documentation/CRD.md).

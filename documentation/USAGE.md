# **Usage**

## Configuring

### Scalable
Within the `rating-operator` deployment is included a basic configuration compatible with standard `metering-operator`:

```sh
$ kubectl get ratingrules.rating.alterway.fr
NAME                          AGE
rating-rating-default-rules   46m

$ kubectl describe ratingrules.rating.alterway.fr rating-rating-default-rules
[...]
Spec:
# The "Metrics" part describe the location of the metric in the metering-operator
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
For more advanced use cases, we strongly advice to create new configurations. To understand why, read the *configuration versionning* part of [this document](/documentation/FEATURES.md) document.

More information on `RatingRules` can be found in the [custom resources documentation](/documentation/CRD.md).

### Reactive

The `rating-operator` also deploys a base configuration for the reactive component. This configuration takes the form of ReactiveRules, describing the same metrics as above, with a lower latency.

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

This example is here to illustrate how both system can supplement each other.

ReactiveRules are not subject to configuration versionning.
More informations on `ReactiveRules` can be found in the [custom resources documentation](/documentation/CRD.md).

----

## Adding new metrics

#### *With metering-operator*

To generate a metric to be rated by rating-operator, follow the instructions [here](https://github.com/operator-framework/operator-metering/blob/master/Documentation/writing-custom-queries.md) to create new `reports`.
When you are done creating a new `Report`, it will appear as such:
```sh
$ kubectl get reports -n metering
NAME                               QUERY                       SCHEDULE   RUNNING                  FAILED   LAST REPORT TIME       AGE
my-test-report                     pod-rating-cpu-request      hourly     ReportingPeriodWaiting            2020-07-29T14:00:00Z   6m14s
```
Then, add it in a `RatingRules` to start rating your new data.


#### *With reactive-rating*

To rate a new metric with the `reactive-rating`, you first need to create a `ReactiveRule`:
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
  Metric:     (sum(rate(container_memory_usage_bytes[1h])) BY (pod, namespace) + on (pod, namespace) group_left(node) (sum(kube_pod_info{pod_ip!="",node!="",host_ip!=""}) by (pod, namespace, node) * 0)) * on () group_left() usage_memory
  # This is the name of the metric once rated
  Name:       test_metric
  # Only second is supported
  Timeframe:  10s
[...]
```

As soon as the `ReactiveRules` is validated, the `reactive-operator` will start processing frames.
More information on `ReactiveRules` can be found in the [custom resources documentation](/documentation/CRD.md).

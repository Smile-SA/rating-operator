# **rating-operator-api**

Used as the communication interface between the rating components, the `rating-operator-api` is also used to expose metrics to users.

There's two ways to access these metrics:

- By watching the results on our Grafana dashboards.
- By querying this API through the exposed endpoints.

In this document we'll explain how to use these endpoints, with examples and expected parameters.

The endpoints are ordered by their resource (namespace, pods, etc..), and the grammar is similar for each category.

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
| **GET `/metrics/<metric>/rating`**           | Get the rating for a given metric.| Parameters expected : `start`  `end` |
| **GET `/metrics/<metric>/total_rating`**           | Get the aggragated rating for a given metric. | Parameters expected : `start`  `end` |
| **GET `/metrics/<metric>/<aggregator>`**           | Get the rating for a given metric, according to the aggregator. | Available aggregator are: `daily`  `weekly` `monthly` |
| **GET `/metrics/<metric>/todate`**           | Get the rating, from the start of the month to now. | No parameters expected. |
| **GET `/metrics/<metric>/max`**           |Get the max rating for a given metric. | Parameters expected : `start`  `end` |
| **GET `/namespaces`**           | Get a list of namespaces visibile | No parameters expected. |
| **GET `/namespaces/rating`**           | Get the rating on a time period, grouped by namespaces.| Parameters expected : `start`  `end`|
| **GET `/namespaces/total_rating`**           | Get the sum of the rating on a time period, grouped by namespaces.| Parameters expected : `start`  `end`|
| **GET `/namespaces/metrics/rating`**           | Get the rating on a time period, grouped by namespaces and metrics.| Parameters expected : `start` `end`|
| **GET `/namespaces/<namespace>/<aggregator>`**           | Get the rating for a namespace, according to the aggregator.|Available aggregator are: `daily`  `weekly` `monthly`|
| **GET `/namespaces/<namespace>/rating`**           | Get the rating on a time period, for a given namespace.| Parameters expected : `start`  `end`|
| **GET `/namespaces/<namespace>/total_rating`**           | Get the sum of the rating on a time period, for a given namespace.| Parameters expected : `start`  `end`|
| **GET `/namespaces/<namespace>/metrics/<metric>/rating`**           | Get the rating on a time period, for givens namespace and metric.| Parameters expected : `start`  `end`|
| **GET `/pods`**           | Get the list of pods. | Parameters expected : `start`  `end` |
| **GET `/pods/rating`**           | Get pods rating.| Parameters expected : `start`  `end`|
| **GET `/pods/total_rating`**           | Get pods aggregated rating.| Parameters expected : `start`  `end`|
| **GET `/pods/metrics/rating`**           | Get the rating on a time period, grouped by namespaces and metrics.| Parameters expected : `start` `end`|
| **GET `/pods/<pod>/<aggregator>`**           | Get the pods rating by time aggregation.|Available aggregator are: `daily`  `weekly` `monthly`|
| **GET `/pods/<pod>/rating`**           | Get the rating for a given pod.| Parameters expected : `start`  `end`|
| **GET `/pods/<pod>/total_rating`**           | Get the sum of the rating , for a given pod.| Parameters expected : `start`  `end`|
| **GET `/pods/<pod>/metrics/<metric>/rating`**           | Get the rating on a time period, for givens pod and metric.| Parameters expected : `start`  `end`|
| **GET `/pods/<pod>/metrics/<metric>/rating`**           | Get the sum of the rating on a time period, for givens pod and metric.| Parameters expected : `start`  `end`|

----


#### Examples 

- **Simple endpoints**

No parameters required, call the endpoint, get a response.

```sh
$ curl http://127.0.0.1/namespaces
{
    "results":[{"namespace":"kube-system","tenant_id":"default"},{"namespace":"longhorn-system","tenant_id":"default"},{"namespace":"monitoring","tenant_id":"default"},{"namespace":"rating","tenant_id":"default"},{"namespace":"unspecified","tenant_id":"default"}],"total":5

}
```

- **Endpoints with url parameters**

The endpoints using this method will be labelled `[URL]`.

We'll use `/metrics/<metric>/<aggregator>` as an exemple here.

In this query, the time range is handled by the **aggregator**, and the parameters are sent through the url.
```sh
# We use  the 'daily' aggregator for the example.
$ curl http://127.0.0.1/metrics/co2-simulation-eu/daily
{"results":[{"value":15.07968}],"total":1}}
```

- **Endpoints with time range (TR)**

The endpoints using this method will be labelled `[TR]`.

For this example, `/metrics/<metric>/rating` is a perfect choice.
There's no time range specified in this query, so we need to specify it using url encoded parameters.
The default value for those is from two hours to now.

```sh
$ curl http://127.0.0.1/metrics/co2-simulation-eu/rating?start=2024-07-10+10%3A22%3A53.604Z&end=2024-07-10+16%3A22%3A53.604Z
{
    "results":[{"frame_begin":"Wed, 10 Jul 2024 10:23:14 GMT", "metric":"co2-simulation-eu","value":0.62832},{"frame_begin":"Wed, 10 Jul 2024 10:23:50 GMT","metric":"co2-simulation-eu","value":0.62833},
    "total": 2
}
```

- **Endpoint with payload**

The endpoints using this method will be labelled `[PL]`.

These endpoints are the hardest to query, from a user perspective.
They are generally available for resource handling, such as rules or tenant management.
Let's create a RatingRuleModel with cURL as an example:

```sh
$ curl -X POST
       -H "Content-Type: application/json"
       -d '{"query_name": "example_query_name","query_group": "example_query_group","query_template: "exmaple_promql_query"}'
       http://127.0.0.1/templates/add
```



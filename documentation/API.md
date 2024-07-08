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
| **GET `/metrics/<metric_name>/rating`**           | Get the rating for a given metric.| Parameters expected : `start`  `end` |
| **GET `/metrics/<metric_name>/total_rating`**           | Get the aggragated rating for a given metric. | Parameters expected : `start`  `end` |
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
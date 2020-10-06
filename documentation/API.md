# API endpoints

**Every GET endpoints listed below can receive url arguments**

- `start` & `end`
- time format is `%Y-%m-%d %H:%M:%S`

**If no arguments are provided, default values will be used.**

## **Healthcheck**

`/alive`

- The alive endpoint is used to know if the service is running.

## **Rating**

The available endpoints are sorted by category

## **Namespaces**

**GET `/namespaces`**

- Get the list of namespaces.

**GET `/namespaces/rating`**

- Get the rating per namespaces, per hour and per metric.

**GET `/namespaces/total_rating`**

- Get the total rating per namespaces.

**GET `/namespaces/<namespace>/total_rating`**

- Get the total rating of a given namespace.

**GET `/namespaces/<namespace>/rating`**

- Get the price for a given namespace, per hour and per metric.

**GET `/namespaces/<namespace>/pods`**

- Get a list of pods for the given namespace.

**GET `/namespaces/<namespace>/nodes`**

- Get a list of nodes for the given namespace.

**GET `/namespaces/<namespace>/nodes/pods`**

- Get the number of pods hosted on nodes for a given namespace.

## **Metrics**

**GET `/metrics`**

- Get the list of metrics.

**GET `/metrics/<metric>/rating`**

- Get the rating for a given metric, per hour.

**GET `/metrics/<metric>/total_rating`**

- Get the total rating for a given metric.

**GET `/reports/<report>/metric`**

- Get the metric for a given report.

**GET `/metrics/<metric>/report`**

- Get the report for a given metric.

**GET `/metrics/<metric>/last_rated`**

- Get the date of the last rating for a given metric.

## **Pods**

**GET `/pods`**

- Get the list of pods.

**GET `/pods/<pod>/lifetime`**

- Get the start and last update time of a pod.

**GET `/pods/rating`**

- Get the rating for a given pod per hour.

**GET `/pods/total_rating`**

- Get the total rating for a given pod.

**GET `/pods/<pod>/rating`**

- Get the rating for a given pod, per hour and per metric.

**GET `/pods/<pod>/total_rating`**

- Get the total rating for a given pod.

**GET `/pods/<pod>/namespace`**

- Get the namespace for a given pod.

**GET `/pods/<pod>/node`**

- Get the node for a given pod.

## **Nodes**

**GET `/nodes`**

- Get the list of nodes.

**GET `/nodes/rating`**

- Get the rating per nodes, per hour and per metric.

**GET `/nodes/total_rating`**

- Get the total rating per nodes.

**GET `/nodes/<node>/rating`**

- Get the price for a given node, per hour and per metric.

**GET `/nodes/<node>/namespaces`**

- Get the namespaces related to a given node.

**GET `/nodes/<node>/pods`**

- Get the pods hosted on a given node.

**GET `/nodes/<node>/total_rating`**

- Get the total rating of a given node.

**GET `/nodes/<node>/namespaces/rating`**

- Get the rating of the namespaces for a given node, per hour and per metric.

**GET `/nodes/<node>/namespaces/<namespace>/rating`**

- Get the rating of the given namespace for a given node, per hour and per metric.

**GET `/nodes/<node>/namespaces/<namespace>/total_rating`**

- Get the total rating of the given namespace for a given node.

## **Configurations**

**GET `/rating/configs`**

- Get the list of all configurations as object 

**GET `/rating/configs/list`**

- Get the list of all configurations as timestamps

**GET `/rating/configs/<timestamp>`**

- Get the configuration for a given timestamp

**POST `/rating/configs/add`**

- Create a new configuration according to the POST request received
- Expect a `body` object containing `rules`, `metrics` and `timestamp` as json

**POST `/rating/configs/update`**

- Update a configuration according to the POST request received
- Expect a `body` object containing `rules`, `metrics` and `timestamp` as json

**POST `/rating/configs/delete`**

- Delete the configuration according to the POST request received
- Expect a `body` object containing `timestamp`



## **Reactive-rating**

**GET `/prometheus/get`**

- Get the **prometheus-rating.rules** object.

**POST `/prometheus/add`**

- Add the given metric to the **prometheus-rating.rules** object.
- Expect a `body` object containing `group`, `expr`, `record` parameters.

**POST `/prometheus/edit`**

- Edit the given metric from the **prometheus-rating.rules** object.
- Expect a `body` object containing `group`, `expr`, `record` parameters.

**POST `/prometheus/delete`**

- Delete the given metric from the **prometheus-rating.rules** object.
- Expect a `body` object containing `group` and `record` parameters.


## **Multi-tenancy**

**`/signup`**

- Render the `signup` template, send the form to `/signup_user`

**POST `/signup_user`**

- Create the user in the database and provides namespace
- Expects **tenant** and **password**
- **quantity** can also be provided, default to 1

**POST `/login`**

- Render the `login` template, send the form to `/login_user`

**POST `/login_user`**

- Log the user in the application, returns a openned session, and redirect to Grafana
- Expects **tenant** and **password**

**`/logout`**

- Close your actual session

**`/password`**

- Render the template to change current users password

**`/password_change`**

- Change the tenant password
- Expect **tenant**, **old** and **new** parameters.

**GET `/current`**

- Returns the tenant holding the session

**GET `/tenant`**

- Expect **tenant**
- Returns the tenant and its namespaces

**GET `/tenants`**

- Require admin token
- Returns the list of tenants

**POST `/tenants/link`**

- Require admin token
- Link namespaces to a given tenant
- Expect **tenant** and **namespaces** (list of identifiers)

**POST `/tenants/unlink`**

- Require admin token
- Unlink a namespace from its tenants
- Expect **namespace**

**POST `/tenants/delete`**

- Require admin token
- Delete a given tenant and all its associated namespaces
- Expect **tenant**


## **Reactive-rules**

**GET `/reactive/get`**

- Get the given ReactiveRule as JSON
- Expect a `name` parameter

**POST `/reactive/new`**

- Create a new ReactiveRule with the given parameters
- Expect a `name`, `timeframe` and `metric`

**POST `/reactive/edit`**

- Edit an existing ReactiveRule with the given parameters
- Expect a `name`, `timeframe` and `metric`


**POST `/reactive/delete`**

- Delete the given ReactiveRule
- Expect a `name`
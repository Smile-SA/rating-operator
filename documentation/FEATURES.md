# **Features**

## **Operator**

As the name imply, `rating-operator` is an operator, a native Kubernetes program.
The operator pattern helps creating and managing [**Custom Resources**](/documentation/CRD.md) natively, aswell as integrating them easily in the Kubernetes ecosystem.

### *Multiple operator*

We decided to use multiple operators, to ensure some important aspect:

- Deployment, version updates and configuration modification is handled by the `rating-operator` itself. It watches `ratings` resources, and deploy rating stacks accordingly. Any modification made to a `rating` resource will triggers changes in the related stack.
- Reactivity to events and custom resources manipulation is handled by the `rating-operator-core` operator.
- The data frames processing ability are provided by the `rating-operator-engine` operator.

For more informations on their respectives custom resources, read this [document](/documentation/CRD.md).

---

## **Rating**

In the `rating-operator`, we provide two mechanism to rates your data:

- A **Prometheus** bound system, with a configurable precision, down to the second.
- A **metering-operator** bound system, that is slower, heavier but more scalable (Deprecated)

Depending on use-case, user profile or resources, you can define which rating method should be used.
Both can be run simultaneously with the same [`RatingRules`](/documentation/CRD.md).
The end product of each mechanism is accessible through the same api endpoints, as the only difference between both types of dataframes is the time precision.

### Prometheus based rating

This rating work is done by the `rating-operator-engine` component.

The `rating-operator-api` exposes the latest `RatingRules` values and labels to Prometheus, which can then be used with **PromQL** to generate dataset to be rated. It uses `ReactiveRules` to configure which metrics to process.

```yml
apiVersion: rating.alterway.fr/v1
kind: ReactiveRule
metadata:
  name: reactive-rule-example
spec:
  metric: your_metric_in_prom
  name: example
  timeframe: 10s
```

Once configured, the `rating-operator-engine` will pick up the new configuration and start processing right away.
You can expect to have rated frames after **timeframe** seconds.

More informations on `RatingRules` and `ReactiveRules` can be found [here](/documentation/CRD.md).

---

### Metering-operator based rating (DEPRECATED)

**DISCLAIMER** The metering-operator is now deprecated. The operator is still compatible with it, but no further developpement will be made on the subject.

By using the [**metering-operator**](), we enable a slow but scalable way to rate frames.
It generates data from `Reports` object, which are aggregated frames with configurable datasources, made every hours / days / weeks / months.
The main advantage of such system in the `rating` context is the low volume of data generated. As the precision is relatively low, you can keep track of months of data with a small storage imprint.
An example use case for this mechanism could be as follow:
> As a cluster administrator, I monitor metrics from 5 clusters using Prometheus federation.
It generates an enormous amount of data, that cannot be stored for a long time.
Succeeding in my business requires me to generate KPIs for further exploitation.
With the metering-operator aggregating data from the main Prometheus instance, generating these KPIs becomes easy, and only a matter of configuration.

Essentially, we aim to help keeping only the data that matter.

#### Configuration versionning

As this system targets large clusters and long term data storage, we implemented a configuration versionning system that ensure to always rate a frame with the correct set of rules.
When first deploying the `rating-operator`, two rulesets are created:

- An immutable one, referenced as "0". Is is a base configuration which ensure basic metrics are capable to be rated without further tweaking.
- The first `RatingRule`, that is referenced by its creation time (as timestamp)

For any frames with a timestamp between **0** and **1596096544**, the configuration 0 will be used. Then for every frames above **1596096544**, configuration **1596096544** is used, until a new configuration is created.

```sh
# The mounted volume holding the configurations, in the rating-operator-api pod
$ ls /config/rates
0           1596096544
```

Every new `RatingRule` that you create will be added to this volume.
Everytime a dataframe is received, the operator will match the corresponding configuration with the timestamp of the metric, before attempting to rate it.

In case of a need to re-trigger the rating for any reason, it ensure your data will be valid.
To re-trigger the processing of all the frames according to new rules, proceed as follow:

- Edit the rules you want
- Remove the `RatedMetric` associated with the metric you are looking to process

The operator will then do all the work again applying the new configurations.

Below an example of this behavior:
> I have one year worth of data stored, with a different configuration each month.
February configuration was faulty but we realised only in May.
Editing the february `RatingRule` and removing the `RatedMetrics` with `$ kubectl delete ratedmetrics.rating.alterway.fr <yourmetric>` will regenerate all the associated data in the next batch.

For more informations on `RatedMetrics` and `RatingRules`, read this [document](/documentation/CRD.md)

## API

We provide `rating-operator-api`, an interface to fetch rated data, handle CustomResources and tenants, that is also used for the internal communications of the `rating-operator`.

You can expose the api locally to try it out with:

```sh
# Exposes the api ports
$ kubectl -n $RATING_NAMESPACE get pods -l app.kubernetes.io/component=api -o name | cut -d/ -f2 | xargs -I{} kubectl port-forward {} 5012:5012

# On another terminal
$ curl http://localhost:5012/alive                                                               
I'm alive!
```

The API, endpoints and way to query are described in details in the [documentation](/documentation/API.md).

---

## Grafana integration

You can explore your metrics through Grafana.
All our endpoints can be used to build dashboards, or explored through the interface.

We provide three distinct dashboards:

- Cloud costs
- Application performance
- Default

These dashboards are provided as example of what can be done.
For additional needs, like adding specifics endpoints to fit a use-case, refer to the [contributing document](/documentation/CONTRIBUTING.md).

In case you did install **Prometheus** with our configuration, ignore the following point.

### Configure Grafana

**DISCLAIMER** If you installed **Prometheus-operator** or **Grafana** through our scripts, skip this step.

To add the `rating-operator-api` as a datasource:
You can setup your Grafana with those two steps:

- Have the proper Grafana version (7.0.3 at time of testing)
- Have Simpod-JSON-datasource plugin installed

Edit the Grafana deployment as follow:

```yml
$ kubectl edit deployments.apps -n monitoring prometheus-grafana
[...]
# Add this line to install the plugin
- env:
  - name: GF_INSTALL_PLUGINS
    value: simpod-json-datasource
[...]
# Change the image tag to the deployment
image: grafana/grafana:7.0.3-ubuntu
```

Once this change is made, save and exit, wait for the pods to restart.
Expose Grafana with the `./hack/forward-grafana` then open `localhost:3000` in a browser.
For a default installation, admin credentials are:

- Login: admin
- Password: prom-operator

Once logged in, add a new datasource with following parameters:

```yaml
# In our case http://rating-operator-api.rating.svc.cluster.local:80
url: http://yourservice.yournamespace.svc.cluster.local:yourport
Whitelist cookie: session
With credentials: true
```

Validate and exit this page, the datasource is ready to be used!

---

### Log in Grafana

The `rating-operator` create a base account for non-registered Grafana users with following credentials:

- Login: default
- Password: default

Those credentials allow you to query every public data generated by the operator.

## Multi-tenant

Natively, all the data generated by both rating mechanism is public, and can be accessed by anyone.
If the context requires data segregation, we provide a mechanism (Local or through an existing Keycloak in your cluster), to authenticate your users (tenants) and assign them namespaces.

A logged in tenant can only access data coming from its namespaces.
Any tenant registered to the application have a Grafana account with the same credentials.

As a tenant, it is required to log in through the `/login` endpoint of `rating-operator-api`, to open your session (as a cookie).

Once logged in, you will be redirected and logged in to Grafana.

Use the `/logout` endpoint to close your session (Logging out from Grafana will not close it)

**DISCLAIMER** Login with your account directly via Grafana will not enable multi-tenant, and you will not be able to query your personnal data. Always use the `/login` of the `rating-operator-api`.

### Local tenants

An administrator can provide accounts for its tenants, by using the `/signup` endpoint. It will help provisioning namespaces to tenants.

Tenants that are handled locally are stored in the database, and updated dynamically by `rating-operator-core`

The `rating-operator-core` handle the tenants / namespaces associations through labels.
By default, every namespaces that doesn't hold the `tenant` labels is public. Attributing this labels yourself will trigger the link between the indicated tenant and labeled namespace.
On Openshift, it uses the `openshift.io/requester` annotations OR the `tenant` label.

### Through Keycloak

**DISCLAIMER** Tested only in Openshift, with a Keycloak synchronizing **users.user.openshift.io** to **projects.project.openshift.io**.

If you configured your `rating-operator` to interact with a Keycloack hosted in your cluster, the user management is handed to Keycloak.
Through the `/login` endpoint of the `rating-operator-api`, keycloak will be used to provide a token, later used in the queries.
The main difference between both system is that tenant:password and tenant:namespaces couples do not exist in database anymore.
If you do not sync users and projects with keycloak, it will not work.
We plan to overhaul this part soon, so expect changes.

---

## Convenience scripts

The `hack` folder is filled with utility scripts to help you use the `rating-operator`:

- `create-regcred` helper to create deployments secrets
- `forward-api` exposes the api locally to port **5012**
- `forward-postgresql` exposes the database to port **5432**
- `forward-prometheus` exposes Prometheus instance to port **9090**
- `forward-alertmanager` exposes AlertManager to port **9093**
- `forward-grafana` exposes Grafana to port **3000**
- `forward-presto` exposes presto to port **8080**
- `hive-cli` run the internal hive cli
- `presto-cli` run the presto cli, to verify reports data

# **Features**

## **Operator**

As the name imply, `rating-operator` is an operator, a native Kubernetes program.
The operator pattern helps us create and manage [**Custom Resources**](/documentation/CRD.md) natively, and integrate them easily in the Kubernetes ecosystem.

### *Resiliency*

Being an operator also means using the resiliency features offered by the platform.
Declaring the desired state of an opertor and the resource it uses, and letting Kubernetes handling its lifecycle is what makes it so powerful.
Be it with deployment, statefulset and other resources, the resiliency brought by Kubernetes is game changing.

### *Replicas*

Being an operator also means scaling capabilities, by replicating our pods and splitting the workload as needed. We used [kopf]() and/or [operator-sdk]() to create the `rating-operator` components, as they include those capabilites natively.

### *Dual operator pattern*

We decided to use a Dual operator pattern, a bit like [metering-operator]() to ensure multiple important aspect:
- Deployment, version updates and configuration modification is handled by the `Rating-operator` itself. It watches `Ratings` resources, and deploy rating stacks accordingly.  Any modification made to a `Rating` resource will triggers changes in the related stack.
- Reactivity to events, processing of dataframes and custom resources manipulation is handled by `Rating-processing` operator. This operator is doing the heavy workload.

For more informations on their respectives custom resources, read this [document](/documentation/CRD.md).

---

## **Rating**

In the `rating` stack, we include two ways to rates your data.
Depending on use-case, user profile or resources, you can define which rating method should be used.
Both can be run simultaneously with the same [`RatingRules`](/documentation/CRD.md).
The end product of each mechanism is accessible through the same api endpoints, as the only difference between both types of dataframes is the time precision.

### Slow but scalable

By using the [**metering-operator**](), we enable a slow but scalable way to rate frames.
It generates data from `Reports` object, which are aggregated frames with configurable datasources, made every hours (up to months).
The main advantage of such system in the `rating` context is the low volume of data generated. As the precision is relatively low, you can keep track of months of data for a small storage imprint.
An example use case for this mechanism could be as follow:
> As a cluster administrator, I monitor metrics from 5 clusters using Prometheus federation.
It generates an enormous amount of data, that cannot be stored for a long time.
Succeeding in my business requires me to generate KPIs for further exploitation.
With the metering-operator aggregating data from the main Prometheus instance, generating these KPIs becomes easy, and only a matter of configuration.

Essentially, we aim to help keeping only the data that matter.

#### Configuration versionning

As this system targets large clusters and long term storage of KPIs, we implemented a configuration versionning system to be sure to always rate a frame with the correct set of rules.
When first deploying the `rating-operator`, two rulesets are created:
- An immutable one, referenced as "0". Is is a base configuration which ensure basic metrics are capable to be rated without further tweaking.
- The first `RatingRule`, that is referenced by its creation time (as timestamp)

For any frames with a timestamp between **0** and **1596096544**, the configuration 0 will be used. Then for every frames above **1596096544**, configuration **1596096544** is used, until a new configuration is created.

```sh
# The mounted volume holding the configurations
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


### Fast and reactive

This system does not require the `metering-operator`, and can be precise down to the second.
It also uses `RatingRules`, but in a different way. The `rating-api` exposes the latest `RatingRules` to Prometheus, which can then be used with PromQL to generate rated frames.
In this context, the configuration versionning system makes no sense, and thus is not available.

It uses `ReactiveRules` to configure which metrics to process.
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

Once configured, the `reactive-rating` will pick up the new configuration and start processing right away.
You can expect to have rated frames after <timeframe> seconds.

More informations on `RatingRules` and `ReactiveRules` can be found [here](/documentation/CRD.md).

---

## API

We provide an API that you can connect to, `rating-api`. It is only accessible from the cluster when deployed, we're letting you expose it via services to fulfill your needs.
It is also used for the internal communications of the `rating-operator`.
Some endpoints requires you to have administrator tokens. You can configure the administrator token at deployement.

You can expose the api locally to try it out with:
```sh
$ kubectl -n $RATING_NAMESPACE get pods -l app.kubernetes.io/component=api -o name | cut -d/ -f2 | xargs -I{} kubectl port-forward {} 5012:5012
$ curl http://localhost:5012/alive                                                               
I'm alive!
```
The available endpoints are documented [here](/documentation/API.md).

---

## Grafana integration

You can explore your metrics through Grafana.
All our endpoints can be used to either build a dashboard that suits your use-case, or explored through the interface.

In case you did install **Prometheus** with our configuration, ignore the following point.

### Configure Grafana

To add the `rating-api` as a datasource:
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
Once this change are made, save and exit, wait for the pods to restart and you are ready.
Expose Grafana with the `./hack/forward-grafana` then open `localhost:3000` in your favorite browser.
For a default installation, admin credentials are:
- Login: admin
- Password: prom-operator

Once logged in, add a new datasource with following parameters:

```
# In our case http://rating-api.rating.svc.cluster.local:80
url: http://yourservice.yournamespace.svc.cluster.local:yourport
Whitelist cookie: session
With credentials: true
```
Validate and exit this page.
Your datasource is ready to be used!

---
### Log in Grafana

The `rating-operator` create a base account for non-admin Grafana users with following credentials:
- Login: default
- Password: default

Those credentials allow you to query every public data generated by the operator.

## Multi-tenant

Natively, all the data generated by both rating mechanism are public, and can be accessed by anyone.
In case you require data segregation, you can create users directly through the api (`/signup`).
When doing so, one (or more) namespace is generated and associated with the user.
A Grafana account is also created, with the same credentials.
All the data generated by these namespaces is considered private and owned by the user.

For a user to access its data, it is needed to log in with the `/login` endpoint of the api, which will provide a **session**. This session will be recognized by the `rating-api` and used to only provide personnal data.
The administrator is in charge of the RBAC / right allocation to go with each namespace using this system.

By using the `/login` endpoint, you will be logged into the `rating-api` AND `Grafana`, and redirected to your dashboard.
Consulting data on Grafana will then only show the data associated with the account.
Use `/logout` to exit the session.

**DISCLAIMER** Login with your account directly via Grafana will not enable multi-tenant, and you will not be able to query your personnal data. Always use the `/login` of the `rating-api`.
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

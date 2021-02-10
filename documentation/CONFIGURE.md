# **CONFIGURATION**

In this document will be described the configuration options made available to the user.

Configuration can be done at different levels, be it prior to build, prior to deployment or at runtime.
Depending on the type of usage you are planning to do, we recommand configuring a different part of the application:

- At the runtime (`./watches.yaml`), to configure environment variable overriding.
- At the operator level (`./deploy/crds/charts.helm.k8s.io_v1alpha1_rating_cr.yaml`), to modify the base configuration at deployment.
- At the top level (`./values.yaml`), to configure the chart deployment.
- At the image level (`./helm-charts/rating/values.yaml`), to provision a base config for the application.

In a last part, we'll describe the external configuration we provide:

- A Prometheus configuration (`./quickstart/prometheus/values.yaml`)
- A Grafana configuration (`./quickstart/grafana/values.yaml`)

## Files descriptions

### Values.yaml

This is the common value file, containing what will be used to generate the rating-operator manifests from the templates located in `./helm-charts/rating`.

```yml
## The security part of the configuration is related to your cluster authentication method (cert files, token, non local users management)
security:
  # The "auth" flag enables TLS/HTTPS verification in the component
  # Enable it if your cluster uses HTTPS
  auth: "true"

  # The "adminToken" string configure the application security key
  # It is used for administrator requests to the rating-api and as a secret key for session encoding
  token:
    admin: thisisadmintoken

  # Keycloak can be used as an authentication method through the operator.
  # Setting enabled to "false" will configure the rating-operator to use its own local user management
  keycloak:
    enabled: "true"

    ## Below the configuration for the Keycloak server
    serverUrl: your_url
    clientID: rating-operator
    realmName: your_realm
    clientSecretKey: "random_secret_key"

## Location of the prometheus component
prometheus:
  service: prometheus-prometheus-oper-prometheus
  namespace: monitoring

## Configuration of the api component
api:

  # Pod name 
  name: api

  # Below lies the name of the postgresql pod running along the rating-api
  config:
    postgres_hostname: "{{ .Release.Name }}-postgresql-headless"
    postgres_secret: "{{ .Release.Name }}-postgresql"

  # Image tags
  # These options are mostly for developpers
  # Base values should satisfy user needs
  image:
    pullPolicy: Always
    repository: hub.rnd.alterway.fr/overboard/5gbiller/rating-api
    tag: master

  # Resources allocation
  # Leaving empty is fine, use only if you know what you are doing, as lack of resources can starve the operator
  affinity: {}
  nodeSelector: {}
  resources: {}
  tolerations: []

  # Rating-api service configuration
  # To be used to expose the api to the web
  service:
    port: 80
    type: ClusterIP
  
  # The rating-operator supports rook-ceph-block and longhorn storageClasses out of the box
  # Follow the rating-operator documentation for more details about their installation and configuration.
  # Different storageClass / provider could be used, but we do not warranty positive results.
  storage:
    storageClass: longhorn

# This value configuration where to reach the metering-operator storage system
# Do not modify if you don't have a specific need
# The usage of metering-operator is deprecated
metering:
  presto_database_uri: presto://root@presto.metering:8080/hive/metering

# Storage pod configuration
# Uses a compressed bitnami/postgresql chart
# See https://github.com/bitnami/charts/blob/master/bitnami/postgresql/values.yaml for more options
postgresql:
  enabled: true
  
  # As mentionned above, rating-operator support rook-ceph-block and longhorn out of the box
  storageClass: longhorn

  # Both password and PostgresPassword have to be set if your postgresqlUsername is "postgres"
  postgresqlUsername: postgres
  postgresqlPassword: notasecret
  postgresqlPostgresPassword: notasecret

  # Openshift/OKD specifics
  # Modify only if you have trouble allocating / RBAC problems with your storage pod on Openshift
    enabled: true
    fsGroup: 1000600000
    runAsUser: 1000600000
  volumePermissions:                                                                                                                                                               
    enabled: false
      runAsUser: 1000600000

## Configuration of the processing component
processing:

  # Pod name
  name: processing

  # Image tags
  # Mostly for developpers, the base values should satisfy user needs
  image:
    pullPolicy: Always
    repository: hub.rnd.alterway.fr/overboard/5gbiller/processing-operator
    tag: master

  # Resources allocation
  # Leaving empty is fine, use only if you know what you are doing, as lack of resources can starve the operator
  affinity: {}
  nodeSelector: {}
  resources: {}
  tolerations: []

## Configuration of the reactive component
reactive:
  
  # Pod name
  name: reactive

  # Image tags
  # Mostly for developpers, the base values should satisfy user needs
  image:
    pullPolicy: Always
    repository: hub.rnd.alterway.fr/overboard/5gbiller/reactive-operator
    tag: master

  # Resources allocation
  # Leaving empty is fine, use only if you know what you are doing, as lack of resources can starve the operator
  affinity: {}
  nodeSelector: {}
  resources: {}
  tolerations: []

## Configuration of the frontend component 
# Grafana is used as the base frontend for the rating-operator
frontend:

  # The address to which you'll be redirected once logged in through the rating-operator
  url: "your_grafana_url"

  # If you try to connect a different frontend to the application, this might be needed
  allowOrigin: "*"

  # Grafana configuration
  grafana:

    # Password for the administrator account
    password: admin

    # The address toward which the requests made to Grafana will be directed
    backend: your_grafana_url

    # Helpers for cookies
    # Grafana session through HTTPS requires specific cookie handling
    env:
      domain: "your_domain"
      httponly: "true"
      secure: "true"
      samesite: "none"


# Convenience options, usually left as default
rbac:
  create: true
service:
  port: 80
  type: ClusterIP
nameOverride: null
networkPolicy:
  enabled: false
fullnameOverride: null
ingress:
  annotations: {}
  enabled: false
  hosts:
    - host: chart-example.local
      paths: []
  tls: []
```

### Watches.yaml

Watches overrides variables at runtime depending on the environment.
If you need to change the base configuration of the application without any pod manipulation,
edit the environmnent variables in the rating-operator pods.
If the variable exist in this file, and in the pods, it can be overrided.
The path in this file has to match the path in the value file used. As an example:

```yml
security:
  auth: "true" # This
```

```yml
- version: v1alpha1
  group: charts.helm.k8s.io
  kind: Rating
  chart: helm-charts/rating
  overrideValues:
    security.auth: ${CLUSTER_AUTH} # Can be overriden by that, by setting CLUSTER_AUTH env var
    security.token.admin: ${RATING_ADMIN_API_KEY}
    api.pullSecretsName: ${PULLSECRETS_API}
    processing.pullSecretsName: ${PULLSECRETS_PROCESSING}
    reactive.pullSecretsName: ${PULLSECRETS_REACTIVE}
    frontend.pullSecretsName: ${PULLSECRETS_FRONTEND}
    postgresql.postgresqlPassword: ${POSTGRESQL_PASSWORD}
    frontend.url: ${FRONTEND_URL}
    frontend.allowOrigin: ${ALLOW_ORIGIN}
    grafana.enabled: ${GRAFANA}
    grafana.backend: ${GRAFANA_BACKEND_URL}
    grafana.password: ${GRAFANA_ADMIN_PASSWORD}
```

## Specifics 

After the common configuration overview above, those shorter explanations will help you decide where you want to include your configuration.

#### Runtime

If a value from the chart have to evolve while already deployed, the best way to do so is to use `kubectl set env`.

Once you have modified the variable, the watch mecanism while forward the change through the application and hold it as its new default.
Pods affected by the change will restart to include the modification.

This is aimed for potential operators wanting to influence rating-operator configuration.

#### Operator level

The operator configuration file, `./deploy/crds/charts.helm.k8s.io_v1alpha1_rating_cr.yaml`, will take the lead on configuration.
Every value that is present in both this file and in the `helm-chart/rating/values.yaml` will be overriden.

This file is the highest in the `values.yaml` hierarchy.

This file is aimed to **end-users**.

#### Top level

The chart configuration file, `values.yaml`, will not be overrided by the above configurations, as deploying as a chart doesn't include those features.

This file is more fore testing, as we don't recommand deploying the operator this way.

#### Image level

This is the lowest level configuration. Every modification made in this file will be embarked in the image you will deploy through the operator.
Obviously, any changes made here requires the rebuilding of the image.

This is aimed at people who will distribute versions of the rating-operator to their users.
An example of that would be including the `Keycloak` and `postgresql` configuration of the company, then letting different services configure their own instance through the `./deploy/crds/charts.helm.k8s.io_v1alpha1_rating_cr.yaml`.

We do not recommand modifying this configuration if you are in a different case.

### Prometheus & Grafana

#### Stack Prometheus

The configuration described below can be found in `./quickstart/prometheus/values.yaml`.

```yaml
# This is the base configuration for the prometheus-operator
# Use the quickstart/grafana/values.yaml if you already have a prometheus and want a local grafana instead
# See https://github.com/helm/charts/blob/master/stable/prometheus-operator/values.yaml for more infos on available options
prometheus:
  prometheusSpec:
    retention: 30d
grafana:
  adminPassword: prom-operator
  sidecar:
    datasources:
      # Keep the default prometheus datasource
      defaultDatasourceEnabled: True
  image:
    repository: grafana/grafana
    tag: 7.3.5
    pullPolicy: IfNotPresent
  # The plugins below are required by the rating-operator datasource
  # Feel free to add more
  plugins:
    - digrich-bubblechart-panel  # Required
    - grafana-clock-panel  # Required
    - simpod-json-datasource  # Required
    - grafana-piechart-panel  # Required
  grafana.ini:
    panels:
      disable_sanitize_html: true
  # Basic datasource configuration for the rating-operator
  datasources:
    datasources.yaml:
      apiVersion: 1
      datasources:
        - name: Rating-operator
          type: simpod-json-datasource
          access: proxy
          # Update the url if you are not running the default configuration
          url: http://rating-api.rating.svc.cluster.local:80
          editable: true
          # Both withCredentials and session cookies are mandatory to exploit the multi-tenant aspect on Grafana
          withCredentials: true
          jsonData:
            keepCookies: ["session"]
  # Dashboards are directly included in the configuration, to ease the deployment
  dashboardProviders:
    dashboardproviders.yaml:
      apiVersion: 1
      providers:
      - name: 'default'
        orgId: 1
        folder: 'admin'
        type: file
        disableDeletion: true
        editable: true
        options:
          path: /var/lib/grafana/dashboards/default
      - name: 'admin'
        orgId: 1
        folder: 'admin'
        type: file
        disableDeletion: true
        editable: true
        options:
          path: /var/lib/grafana/dashboards/admin
      - name: 'tenant'
        orgId: 1
        folder: ''
        type: file
        disableDeletion: true
        editable: false
        options:
          path: /var/lib/grafana/dashboards/tenant
  dashboards:
    [...]
```

#### Grafana

The Grafana configuration is included in the Prometheus one. Please refer to the above.

The configuration for the standalone Grafana installation is located at `./quickstart/grafana/values.yaml`.

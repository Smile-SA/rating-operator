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
    auth: "false"

    # The "adminToken" string configure the application security key
    # It is used for administrator requests to the rating-operator-api and as a secret key for session encoding
    token:
      admin: thisisadmintoken

    # The "adminAccount" variable defines the which tenant is considered super-admin.
    # Usually, the default "admin" is enough. Some external applications already using the "admin" name could motivate to change this parameter.
    # Don't forget to edit the Grafana deployment accordingly, to syncronise both adminAccount values.
    # the super-admin account password is the same with Grafana password 
    adminAccount: admin

    # To authentication users in Rating operator three options are possible
    # Choose one authentication option from the three options (local/ldap/keycloak)

    authentication_type: ldap

    #  If you set authentication_type to ldap, set the following configuration information of keycloak
    ldap:
      ## Below the configuration for the ldap server
      serverUrl: "ldap://openldap.ns1.svc.cluster.local:389"
      adminpassword: ""
      ldap_schema: "ou=Tenants,dc=example,dc=org"

    # If you set authentication_type to keycloak, set the following configuration information of keycloak
    keycloak:
      ## Below the configuration for the Keycloak server
      # serverUrl: "http://keycloak.default.svc.cluster.local:8080/auth/"
      # clientID: Rating
      # realmName: "Rating operator"
      # clientSecretKey: "your client secret key"

  ## Location of the prometheus component
  prometheus:
    service: prometheus-kube-prometheus-prometheus
    namespace: monitoring
    schema: http
    domain: svc.cluster.local
    port: 9090

  ## Configuration of the api component
  api:

    # Pod name 
    name: api

    # Below lies the name of the postgresql pod running along the rating-operator-api
    config:
      postgres_hostname: "{{ .Release.Name }}-postgresql-headless"
      postgres_secret: "{{ .Release.Name }}-postgresql"

    # Image tags
    # These options are mostly for developpers
    # Base values should satisfy user needs
    image:
      pullPolicy: Always
      repository: hub.rnd.smile.fr/overboard/5gbiller/rating-operator-api
      tag: master-test-2

    # Resources allocation
    # Leaving empty is fine, use only if you know what you are doing, as lack of resources can starve the operator
    affinity: {}
    nodeSelector: {}
    resources: {}
    tolerations: []

    # rating-operator-api service configuration
    # To be used to expose the api to the web
    service:
      port: 80
      type: ClusterIP
    
    # The rating-operator supports rook-ceph and longhorn storageClasses out of the box
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
  global:
    storageClass: longhorn
    postgresql:
      storageClass: longhorn
  storageClass: longhorn
  postgresql:
    enabled: true
    
    # As mentionned above, rating-operator support rook-ceph and longhorn out of the box
    storageClass: longhorn

    # Both password and PostgresPassword have to be set if your postgresqlUsername is "postgres"
    postgresqlUsername: postgres
    postgresqlPassword: notasecret
    postgresqlPostgresPassword: notasecret

    # Openshift/OKD specifics
    # Modify only if you have trouble allocating / RBAC problems with your storage pod on Openshift
    # securityContext:                                                                                                                                                                 
    #   enabled: true                                                                                                                                                                  
    #   fsGroup: 1000600000
    #   runAsUser: 1000600000
    # volumePermissions:                                                                                                                                                               
    #   enabled: false                                                                                                                                                                 
    #   securityContext:                                                                                                                                                               
    #     runAsUser: 1000600000

  ## Configuration of the manager component
  manager:

    # Pod name
    name: manager

    # Image tags
    # Mostly for developpers, the base values should satisfy user needs
    image:
      pullPolicy: Always
      repository: hub.rnd.smile.fr/overboard/5gbiller/rating-operator-manager
      tag: master

    # Resources allocation
    # Leaving empty is fine, use only if you know what you are doing, as lack of resources can starve the operator
    affinity: {}
    nodeSelector: {}
    resources: {}
    tolerations: []

  ## Configuration of the engine component
  engine:
    
    # Pod name
    name: engine

    # Image tags
    # Mostly for developpers, the base values should satisfy user needs
    image:
      pullPolicy: Always
      repository: hub.rnd.smile.fr/overboard/5gbiller/rating-operator-engine
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
    url: "localhost:3000"

    # If you try to connect a different frontend to the application, this might be needed
    allowOrigin: "*"

    # Grafana configuration
    grafana:

      # Password for the administrator account
      password: prom-operator

      # The address toward which the requests made to Grafana will be directed
      backend: "prometheus-grafana.monitoring.svc.cluster.local"

      # Helpers for cookies
      # Grafana session through HTTPS requires specific cookie handling
      env:
        domain: ""
        httponly: "false"
        secure: "false"
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
    manager.pullSecretsName: ${PULLSECRETS_MANAGER}
    engine.pullSecretsName: ${PULLSECRETS_ENGINE}
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

### Runtime

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
          url: http://rating-operator-api.rating.svc.cluster.local:80
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

## Keycloak
To access to the keycloak web interface:

```sh
kubectl port-forward keycloak-pod-name 8080:8080

```
You can then access to: http://localhost:8080

To configure keycloak, follow this resumed steps (see more configuration details in [this page](https://www.keycloak.org/docs/latest/server_admin/)):
1. Start first by creating your realm with a specific name `e.g. rating` (a *realm* manages a set of users, credentials, roles, and groups. A user belongs to and logs into a realm. Realms are isolated from one another and can only manage and authenticate the users that they control.):


<img style="BORDER-TOP-COLOR: #000000; BORDER-LEFT-COLOR: #000000; BORDER-RIGHT-COLOR: #000000;
          BORDER-BOTTOM-COLOR: #000000;" border="5" src="/img/realm.png" width="500">

2. Access to the created realm and click to clients in the left sidebar to create a new client (*clients* are entities that can request Keycloak to authenticate a user. Most often, clients are applications and services that want to use Keycloak to secure themselves and provide a single sign-on solution.). Set the parameters as follows:

      - Access type: confidential
      - Standard flow enabled: OFF
      - Direct access grant: ON

<img src="/img/client.png" width="800">

3. Create a user set the password to not temporary (*users* are entities that are able to log into the rating operator application).

<img src="/img/user.png" width="800">

4. Configure namespaces for the user:

  1. Add the `namespaces` variable for the user in the user attributes:

   <img src="/img/namespaces.png" width="800">
  
  2. Add a mapper to the client, to enable sending this attribute in the user login token:
  
  <img src="/img/mappers.png" width="700">

Once done, you can add the realm, client id and secret in the configuation [file](/deploy/crds/charts.helm.k8s.io_v1alpha1_rating_cr.yaml) as described above.
The client secret can be found in the `credentials` tab:
<img src="/img/key.png" width="580">

**NOTE**: the namespaces should be separated with a dash "-" (e.g. namespaces= "ns1-ns2").

Each created user in keycloak belongs to a group either `admin` or `user`. To specify the group of a user, create the attribute named `group` in keycloak with the same steps as the `namespaces` attribute. Set the value of the `group` attribute to `admin` for admin-user and `user` for a normal user (see types of Rating operator users in his [file](/documentation/CONFIGURE.md)).

## Openldap

Once openldap is deployed (see how to install openldap in this [file](/documentation/install.md)), create the ldap schema following the steps below:

### Create the ldap schema 

1. access to one of the openldap pods:
```sh
kubectl exec -it openldap_pod -- /bin/bash
```

2. Create the `structure.ldif` file containing the following ldap schema: 

```sh
echo "dn: ou=Tenants,dc=example,dc=org
objectclass: organizationalUnit
ou: Tenants

dn: cn=user,ou=Tenants,dc=example,dc=org
objectClass: inetOrgPerson
givenName: user
sn: user
cn: user user
uid: ns1-ns2
userPassword: mdp
" > structure.ldif
```
3. Deploy the `structure.ldif` file:

```sh
ldapadd -x -D 'cn=admin,dc=example,dc=org' -w Not@SecurePassw0rd -H ldapi:/// -f structure.ldif
```
4. Each time you want to create a new user, redo the same steps with the following `structure.ldif` file:
```sh
echo "dn: cn=user,ou=Tenants,dc=example,dc=org
objectClass: inetOrgPerson
givenName: user
sn: admin /or user
cn: user user
uid: ns3-ns4
userPassword: mdp
" > structure.ldif
```

**NOTE**: the namespaces of users are defined in the Object attribute `uid` with the same format as keycloak (i.e. the namespaces should be separated with a dash "-" (e.g. uid: ns1-ns2)).
**NOTE**: you can use the `phpadmin`web interface to do this steps.

Each created user in ldap belongs to a group either `admin` or `user`. To specify the group of a user, set **sn** to `admin` for admin-user and `user` for normal user.

**NOTE**: for the local authentication option, the group of a user is specified while the user account is created in the `api/signup`.

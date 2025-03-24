Karapace
========

This is a packaging of [Aiven Karapace](https://github.com/aiven/karapace) for use as a REST API for Kafka in the NAIS platform together with [Kafkarator](https://github.com/nais/kafkarator).

Aiven uses Karapace to provide a REST API and Schema Registry for their managed Kafka offering. Unfortunately, their setup means that any user with access to the REST API will have full access to all topics regardless of ACLs in use. This is not acceptable for us, so we have created this packaging where teams can deploy Karapace in their own namespaces on the NAIS platform, with credentials that limit it to just the topics they should have access to.

Access control
--------------

<div class="Box Box--danger"><div class="Box-body">

:warning::warning::warning: NOTE :warning::warning::warning:

In order to ensure proper access control for the REST API, the application should be deployed to our GCP clusters, with *no ingress* and strictly configured Access Policies. This is important, as anyone who can *call* your instance of Karapace *will have access to everything* you have access to.

</div></div>


Deploy
------

### 1. Create a new repository with a nais.yaml file:

```yaml
apiVersion: "nais.io/v1alpha1"
kind: "Application"
metadata:
  name: karapace
  namespace: myteam
  labels:
    team: myteam
spec:
  image: ghcr.io/nais/karapace:latest
  liveness:
    path: "/"
  readiness:
    path: "/brokers"
  replicas:
    min: 1
    max: 1
    cpuThresholdPercentage: 50
  prometheus:
    enabled: false
  resources:
    limits:
      cpu: "200m"
      memory: "256Mi"
    requests:
      cpu: "200m"
      memory: "256Mi"
  kafka:
    pool: nav-dev
```

If you want to use a specific version, get the latest karapace image from the [Karapace package page](https://github.com/orgs/nais/packages/container/package/karapace).

### 2. Create a workflow to deploy the application and configmap

```yaml
name: "Deploy Karapace"
on:
  push:
    branches:
    - "main"
jobs:
  deploy:
    name: "Deploy Karapace"
    runs-on: ubuntu-latest
    steps:
      - uses: "actions/checkout@v2"
      - uses: nais/deploy/actions/deploy@v1
        env:
          CLUSTER: dev-gcp
          RESOURCE: nais.yaml
```

### 3. Commit and push

Commit `nais.yaml` and `.github/workflows/main.yaml` and push to github.


Usage
-----

Karapace provides the same API as the Confluent Kafka REST proxy (v1). The [Confluent documentation](https://docs.confluent.io/platform/current/kafka-rest/index.html) should be fairly accurate, but differences may be documented in the [Aiven Karapace project](https://github.com/aiven/karapace). See also this [issue](https://github.com/aiven/karapace/issues/181#issuecomment-828210804).

Karapace will be available using a service address in the cluster (http://application-name.namespace/), assuming you have set proper access policies.

Verifying the Karapace image and its contents
-----

The image is signed "keylessly" using [Sigstore cosign](https://github.com/sigstore/cosign).
To verify its authenticity run
```
cosign verify \
--certificate-identity "https://github.com/nais/karapace/.github/workflows/main.yaml@refs/heads/main" \
--certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
ghcr.io/nais/karapace@sha256:<shasum>
```

The images are also attested with SBOMs in the [CycloneDX](https://cyclonedx.org/) format.
You can verify these by running
```
cosign verify-attestation --type cyclonedx \
--certificate-identity "https://github.com/nais/karapace/.github/workflows/main.yaml@refs/heads/main" \
--certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
ghcr.io/nais/karapace@sha256:<shasum>
```


Development
-----------

After making changes, karapace will be deployed to the nais namespace of nav-dev-gcp for testing.
Using mise, you can run a simple integration test:

```shell
mise run integration-test
```

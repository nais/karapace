Karapace
========

This is a packaging of [Aiven Karapace](https://github.com/aiven/karapace) for use as a REST API for Kafka in the NAIS platform together with [Kafkarator](https://github.com/nais/kafkarator).

Aiven uses Karapace to provide a REST API and Schema Registry for their managed Kafka offering. Unfortunately, their setup means that any user with access to the REST API will have full access to all topics regardless of ACLs in use. This is not acceptable for us, so we have created this packaging where teams can deploy Karapace in their own namespaces on the NAIS platform, with credentials that limit it to just the topics they should have access to.

In order to ensure proper access control for the REST API, the application should be deployed to our GCP clusters, with no ingress and strictly configured Istio Access Policies.

Usage
-----

TBD

#!/bin/bash

set -o errexit   # abort on nonzero exitstatus
set -o nounset   # abort on unbound variable
set -o xtrace    # echo commands after variable expansion

registry_host="${KAFKA_SCHEMA_REGISTRY%:*}" # Drop port part
registry_port="${KAFKA_SCHEMA_REGISTRY##*:}" # Drop host part
config_path=/tmp/config.json

echo "=== User info"
id

echo "=== Config template"
cat /app/karapace_config.json

jq --null-input \
  --arg advertised_hostname "${NAIS_APP_NAME}.${NAIS_NAMESPACE}" \
  --arg bootstrap_uri "${KAFKA_BROKERS}" \
  --arg client_id "$(hostname)" \
  --arg group_id "${NAIS_CLIENT_ID}" \
  --arg registry_host "${registry_host}" \
  --arg registry_port "${registry_port}" \
  --arg ssl_cafile "${KAFKA_CA_PATH}" \
  --arg ssl_certfile "${KAFKA_CERTIFICATE_PATH}" \
  --arg ssl_keyfile "${KAFKA_PRIVATE_KEY_PATH}" \
  --from-file "/app/karapace_config.json" \
  > "${config_path}"

echo "=== Generated config"
cat "${config_path}"

echo "=== Dropping potentially confusing env-variables"
for v in $(compgen -A export | grep KARAPACE); do export -n "${v?}"; done


exec python3 -m karapace.karapace_all "${config_path}"

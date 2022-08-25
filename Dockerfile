FROM ghcr.io/aiven/karapace:3.3.1
LABEL maintainer=aura@nav.no

RUN apt-get update -y && \
    apt-get install -y jq

COPY karapace_config.json /app/karapace_config.json
COPY launcher.sh /app/.local/bin/

EXPOSE 8081
CMD ["/app/.local/bin/launcher.sh"]

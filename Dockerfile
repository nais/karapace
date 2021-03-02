FROM navikt/python:3.9 as common
LABEL maintainer=aura@nav.no

USER root

RUN apt-get update -y && \
    apt-get install -y jq

FROM common as build

RUN apt-get update -y && \
    apt-get install -y curl git gcc g++ make

ENV KARAPACE_SHA=4737f82cb685444aaa49d6aabb5edc0a6e0392ea

# TODO: Remove version hack when https://github.com/aiven/karapace/issues/157 is fixed
RUN mkdir -p /build && \
    curl --location https://github.com/aiven/karapace/archive/${KARAPACE_SHA}.tar.gz | tar xzv -C /build  --strip-components=1 && \
    echo "__version__ = '2.0.1'" > /build/karapace/version.py
RUN pip wheel -r /build/requirements.txt --no-cache-dir --wheel-dir=/build/wheels/ && \
    pip wheel /build/ --no-deps --no-index --no-cache-dir --find-links=/build/wheels/ --wheel-dir=/build/wheels/

FROM common as production

# Get rid of all build dependencies, install application using only pre-built binary wheels
COPY --from=build /build/wheels/ /app/wheels/

USER apprunner

RUN mkdir -p /app/.local/bin && \
    pip install --user --no-index --no-deps --find-links=/app/wheels/ --only-binary all /app/wheels/*.whl

COPY karapace_config.json /app/karapace_config.json
COPY launcher.sh /app/.local/bin/

EXPOSE 8081
CMD ["/app/.local/bin/launcher.sh"]

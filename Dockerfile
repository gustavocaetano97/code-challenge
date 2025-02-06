# registry.gitlab.com/meltano/meltano:latest is also available in GitLab Registry
ARG MELTANO_IMAGE=meltano/meltano:latest-python3.10
FROM $MELTANO_IMAGE

COPY ./etl_meltano /project

WORKDIR /project

ENTRYPOINT ["meltano"]
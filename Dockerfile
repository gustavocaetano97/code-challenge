# registry.gitlab.com/meltano/meltano:latest is also available in GitLab Registry
ARG MELTANO_IMAGE=meltano/meltano:latest-python3.10
FROM $MELTANO_IMAGE

WORKDIR /project

#ENTRYPOINT ["meltano"]
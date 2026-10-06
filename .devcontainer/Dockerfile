FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm
# Yarn wird im Python-Training nicht verwendet. Die geerbte Paketquelle hat
# einen veralteten Signaturschlüssel und verhindert apt-basierte Features.
RUN rm -f /etc/apt/sources.list.d/yarn.list
COPY --from=ghcr.io/astral-sh/uv:0.12.10 /uv /uvx /usr/local/bin/

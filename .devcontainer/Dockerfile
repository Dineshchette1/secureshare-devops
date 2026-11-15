FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# The base image ships a Yarn apt repo whose GPG key no longer verifies.
# That breaks 'apt-get update', which the devcontainer features rely on.
# We don't use Yarn, so remove the repo before features are installed.
RUN find /etc/apt/sources.list.d -name '*yarn*' -delete
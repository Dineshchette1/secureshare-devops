#!/usr/bin/env bash
# Runs once when the Codespace is created.
set -euo pipefail

mkdir -p "$HOME/.terraform.d/plugin-cache"

python -m pip install --upgrade pip
pip install pre-commit checkov boto3

# Git hooks: terraform fmt, secret detection, etc.
pre-commit install || true

echo ""
echo "Tool versions:"
terraform version | head -1
aws --version
az version --query '"azure-cli"' -o tsv 2>/dev/null | sed 's/^/azure-cli /' || true
docker --version || true
echo ""
echo "Codespace ready. Next: run 'aws sts get-caller-identity' to check your AWS login."
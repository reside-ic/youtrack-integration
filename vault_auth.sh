#!/usr/bin/env bash
set -ex

export VAULT_ADDR='https://support.montagu.dide.ic.ac.uk:8200'
if [ "$VAULT_AUTH_GITHUB_TOKEN" = "" ]; then
    echo -n "Please provide your GitHub personal access token for the vault: "
    read -s token
    echo ""
    export VAULT_AUTH_GITHUB_TOKEN=${token}
fi
echo "Authenticating with the Vault"
export VAULT_TOKEN=$(vault login --method=github --token-only)

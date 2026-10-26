#!/usr/bin/env bash
set -euo pipefail

# Extract Active Node address from 'vault status'. May break if command output changes in future.
ACTIVE_NODE=$(vault status 2>/dev/null | grep -i 'Active Node Address' | awk '{print $4}')

if [ -z "${ACTIVE_NODE}" ]; then
  echo "Error: Unable to find active leader address from vault status." >&2
  exit 1
fi

echo "Active node found: ${ACTIVE_NODE}"

export VAULT_ADDR="${ACTIVE_NODE}"
ts=$(date +%Y%m%d%H%M%S)
vault operator raft snapshot save /tmp/vault-backup-${ts}.snap
aws s3 cp /tmp/vault-backup-${ts}.snap s3://frdrvault-backup-bucket/raft/
rm /tmp/vault-backup-${ts}.snap

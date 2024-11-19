# FRDR Encryption App

## Deploying Vault Locally

See the guide: https://developer.hashicorp.com/vault/tutorials/day-one-raft/raft-deployment-guide

## Create policy on Vault instance

Log into Vault instance with root token.

Create the policy file named frdr-user.hcl

```
# Grant permissions on user specific path for dataset key storage
path "secret/data/dataset/{{identity.entity.id}}/*" {
    capabilities = [ "create", "update", "read", "delete", "list" ]
}

# Grant permissions on user specific path for public key management
path "secret/data/public_key/{{identity.entity.id}}" {
    capabilities = [ "create", "update", "read", "delete", "list" ]
}

# Grant permissions on reading public keys of other uesrs
path "secret/data/public_key/*" {
    capabilities = ["read"]
}

# Grant permissions to edit metadata on user specific path
path "secret/metadata/dataset/{{identity.entity.id}}/*" {
    capabilities = [ "create", "update", "read", "delete", "list" ]
}

# Grant read permission on user specific path under other user's path for dataset key sharing
path "secret/data/dataset/+/+/{{identity.entity.id}}" {
    capabilities = ["read"]
}

# Read entity info of other users
path "identity/entity/id/*" {
  capabilities = [ "read"]
}

# List secrets belong to user
path "secret/metadata/{{identity.entity.id}}" {
  capabilities = ["list" ]
}

# Create encryption key
path "transit/keys/{{identity.entity.id}}" {
    capabilities = [ "create", "read", "update", "list" ]
}

# Generate data key
path "transit/datakey/*" {
    capabilities = [ "create", "read", "update", "list" ]
}

# Use PKI engine to for cert generation, update the path with the correct role name
path "pki_int/issue/frdrvault-dot-net" {
	capabilities = [ "create", "read", "update", "list" ]
}
```

Create a policy named frdr-user with the policy defined in frdr-user.hcl

Enable OIDC auth method: https://developer.hashicorp.com/vault/tutorials/auth-methods/oidc-auth

Enable secrets engine: https://developer.hashicorp.com/vault/tutorials/encryption-as-a-service/eaas-transit

Enable PKI secrets engine for certificate generation: https://developer.hashicorp.com/vault/tutorials/secrets-management/pki-engine

Create a role named frdrvault-dot-net which allows subdomains, and specify the default issuer ref ID as the value of issuer_ref:
`vault write pki_int/roles/frdrvault-dot-net allowed_domains="frdrvault.net" allow_subdomains=true allow_bare_domains=true allow_glob_domains=true max_ttl="720h"`



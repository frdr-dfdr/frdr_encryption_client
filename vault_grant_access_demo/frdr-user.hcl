# Grant permissions on user specific path
path "user-kv/data/{{identity.entity.name}}/*" {
    capabilities = [ "create", "update", "read", "delete", "list" ]
}

# For Web UI usage
path "user-kv/metadata" {
  capabilities = ["list"]
}

path "identity/group/name/{{identity.entity.name}}_*" {
  capabilities = [ "create", "update", "read", "delete", "list" ]
}

# Create and manage policies
path "sys/policies/acl/*" {
  capabilities = [ "create", "read", "update", "delete", "list" ]
}

# Create encryption key
path "transit/keys/*" {
  capabilities = [ "create", "read", "update", "list" ]
}

# Decrypt data
path "transit/decrypt/*" {
  capabilities = [ "create", "read", "update", "list" ]
}
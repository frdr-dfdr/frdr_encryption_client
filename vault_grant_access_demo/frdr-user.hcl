# Grant permissions on user specific path
path "user-kv/data/{{identity.entity.name}}/*" {
    capabilities = [ "create", "update", "read", "delete", "list" ]
}

# For Web UI usage
path "user-kv/metadata" {
  capabilities = ["list"]
}

# Create groups
path "identity/group" {
  capabilities = [ "create", "update", "read", "delete", "list" ]
}

# Create and manage policies
path "sys/policies/acl/*" {
  capabilities = [ "create", "read", "update", "delete", "list" ]
}
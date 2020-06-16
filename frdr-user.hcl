# Grant permissions on user specific path
path "secret/data/{{identity.entity.id}}/*" {
    capabilities = [ "create", "update", "read", "delete", "list" ]
}

# Create and manage groups
path "identity/group/name/{{identity.entity.id}}_*" {
    capabilities = [ "create", "update", "read", "delete", "list" ]
}

# Create and manage policies
path "sys/policy/{{identity.entity.id}}_*" {
    capabilities = [ "create", "read", "update", "delete", "list" ]
}

# Read entity info of other users
path "identity/entity/id/*" {
  capabilities = [ "read"]
}

# Create encryption key
path "transit/keys/*" {
    capabilities = [ "create", "read", "update", "list" ]
}

# Generate data key
path "transit/datakey/*" {
    capabilities = [ "create", "read", "update", "list" ]
}
# Decrypt data
path "transit/decrypt/*" {
    capabilities = [ "create", "read", "update", "list" ]
}
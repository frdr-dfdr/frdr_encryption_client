# Grant permissions on user specific path
path "secret/data/{{identity.entity.id}}/*" {
    capabilities = [ "create", "update", "read", "delete", "list" ]
}

# Grant permissions to edit metadata on user specific path
path "secret/metadata/{{identity.entity.id}}/*" {
    capabilities = [ "create", "update", "read", "delete", "list" ]
}

# Grant read permission on user specific path under other user's path
path "secret/data/+/+/{{identity.entity.id}}" {
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
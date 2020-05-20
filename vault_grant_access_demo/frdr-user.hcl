# Grant permissions on user specific path
path "secret/data/{{identity.entity.name}}/*" {
    capabilities = [ "create", "update", "read", "delete", "list" ]
}

# Create and manage groups
path "identity/group/name/{{identity.entity.name}}_*" {
    capabilities = [ "create", "update", "read", "delete", "list" ]
}

# Create and manage policies
path "sys/policy/{{identity.entity.name}}_*" {
    capabilities = [ "create", "read", "update", "delete", "list" ]
}

# Just use this for demo using CLI commands
path "sys/policies/acl/{{identity.entity.name}}_*" {
    capabilities = [ "create", "read", "update", "delete", "list" ] 
}
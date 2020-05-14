path "identity/group/id" {
  capabilities = [ "list" ]
}

# Group member can update the group information
path "identity/group/id/{{identity.groups.names.bob_dataset1_secret_share_group.id}}" {
  capabilities = [ "update", "read", "create", "delete", "list" ]
}

# Group member can update the group information
#path "identity/group/id/{{identity.groups.names.bob_secret_admin.id}}" {
#  capabilities = [ "update", "read", "create", "delete", "list" ]
#}


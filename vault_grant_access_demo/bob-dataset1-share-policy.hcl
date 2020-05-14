# Grant permissions on the group specific path
# The region is specified in the group metadata


#path "user-kv/data/{{identity.groups.names.bob_dataset1_secret_share_group.metadata.key_path_name}}/{{identity.groups.names.bob_dataset1_secret_share_group.metadata.dataset_uuid}}" {
#    capabilities = [ "read", "list" ]
#}

# path in <user_uuid>/<dataset_uuid> format
path "user-kv/data/bob_smith/dataset1" {
    capabilities = [ "read", "list", "delete"]
}

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
# Use PKI engine to for cert generation, depending on the name of the role created
path "pki_int/issue/frdr-dot-ca" {
    capabilities = [ "create", "read", "update", "list" ]
}
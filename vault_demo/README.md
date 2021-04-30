# Users Grant Temporary Access to Secret Path on Vault
All the operations are done with CLI commands in this demo, which can also be performed with API calls.

1. The symmetric key is encrypted with data author's public key locally with the FRDR encryption app.
2. The encrypted symmetric key is saved on vault on the path `/secret/{author_uuid}/{dataset_uuid}`.
3. When data author wants to share this key with requester, data author needs to
   * retrieve the encrypted symmetric key
   * decrypt it with data author's private key
   * encrypt the symmetric key again with requester's public key
   * before saving to vault, set the metadata `-delete-version-after=360h` of path `/secret/{author_uuid}/{dataset_uuid}/{requester_uuid}`, in which case this key will be deleted automatically in 15 dyas
   * save the new encrypted key on vault on the path `/secret/{author_uuid}/{dataset_uuid}/{requester_uuid}`


## Start the Dev Server
To start the Vault dev server, run:
```sh
vault server -dev
```
With the dev server started, perform the following:
1. Launch a new terminal session.
2. Run the `export VAULT_ADDR ...` command from the terminal output. 
    ```sh
    export VAULT_ADDR='http://127.0.0.1:8200'
    ```
3. Set the `VAULT_DEV_ROOT_TOKEN_ID` environment variable value to the generated Root Token value displayed in the terminal output.
    ```sh
    export VAULT_DEV_ROOT_TOKEN_ID='s.2cS8g8Eps3LIy6Uy0y85z4p0'
    ```
## Create Users for Testing
If you have two users for testing, add the following policy "frdr-user" to entities, then skip this step.

Login with root token 
```sh
vault login $VAULT_DEV_ROOT_TOKEN_ID
```

Enable the `userpass` auth method. 
```sh
vault auth enable userpass
```
Retrieve the userpass mount accessor and save it in a file named `accessor.txt`.
```sh
vault auth list -format=json | jq -r '.["userpass/"].accessor' > accessor.txt
```
Create a new policy called `frdr-user`, which will be attached to the testing users.

frdr-user.hcl
```yaml
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
```
```sh
vault policy write frdr-user frdr-user.hcl
```
Create new users, "bob" and "alice" with password "training"
```sh
vault write auth/userpass/users/bob password="training" policies="frdr-user"
vault write auth/userpass/users/alice password="training" policies="frdr-user"
```
Create new entities `bob_smith` and `alice_smith` for testing. "bob" and "alice" are not entity names, they are the account name when using userpass auth. If we do not create entities manually, then the entity will be created automatically the user logs into the Vault. The generated entity_name is something like this "entity_c2e598ec". To make the demo clear, we will create an entity with a meaningful name. However, in the implementation for our project, we prefer to keep the original entity name. 

```sh
# Create a bob_smith entity and save the identity ID in the entity_id.txt.
vault write -format=json identity/entity name="bob_smith" policies="frdr-user" | jq -r ".data.id" > bob_entity_id.txt
# Add an entity alias for the bob_smith entity.
vault write identity/entity-alias name="bob" canonical_id=$(cat bob_entity_id.txt) mount_accessor=$(cat accessor.txt)

vault write -format=json identity/entity name="alice_smith" policies="frdr-user" | jq -r ".data.id" > alice_entity_id.txt
vault write identity/entity-alias name="alice" canonical_id=$(cat alice_entity_id.txt) mount_accessor=$(cat accessor.txt)
```

## Test on Saving Secrets and Sharing with Other Users
A key/value v2 secrets engine at path `secret` has been enabled when starting the server in dev mode.

Now we are having two users, `alice` with entity_id `7c320c35-a681-d4ee-3339-7381dd91ac9d`, and `bob` with entity_id `6644aeb0-ce1d-a256-c48e-d81702c487cb`

Log in as alice (data author)
```sh
vault login -method=userpass username="alice" password="training"
```
Write the encrypted symmetric key of dataset1 to alice's secret path `/secret/{alice_uuid}/{dataset_uuid}`. She is the only user having access to it.
```sh
vault kv put secret/7c320c35-a681-d4ee-3339-7381dd91ac9d/dataset1 key=1234
```
To share with bob, write the new encrypted symmetric key, which is encrypted with bob's public key, to another path `/secret/{alice_uuid}/{dataset_uuid}/{bob_uuid}` on valut. 
Set the metadata first since it specifies the deletion_time for all new versions written to this path. (The metadata is set to delete this key in 5 min for demo purpose.)
```sh
vault kv metadata put -delete-version-after="5m" secret/7c320c35-a681-d4ee-3339-7381dd91ac9d/dataset1/6644aeb0-ce1d-a256-c48e-d81702c487cb
vault kv put secret/7c320c35-a681-d4ee-3339-7381dd91ac9d/dataset1/6644aeb0-ce1d-a256-c48e-d81702c487cb key=5678
```
Log in as "bob", and try to read secret on path `/secret/{alice_uuid}/{dataset_uuid}/{bob_uuid}`
```sh
vault login -method=userpass username="bob" password="training"
vault kv get secret/7c320c35-a681-d4ee-3339-7381dd91ac9d/dataset1/6644aeb0-ce1d-a256-c48e-d81702c487cb
```
We can see from the output that bob can read the secret saved on this path, but the secret will be deleted 5 mins after created.
```
====== Metadata ======
Key              Value
---              -----
created_time     2021-04-30T23:16:06.625561Z
deletion_time    2021-04-30T23:21:06.625561Z
destroyed        false
version          1

=== Data ===
Key    Value
---    -----
key    5678
```
Try to read the secret in several minutes, the output will be 
```
====== Metadata ======
Key              Value
---              -----
created_time     2021-04-30T23:16:06.625561Z
deletion_time    2021-04-30T23:21:06.625561Z
destroyed        false
version          1
```
Let's see if bob can read the original encrypted key saved on path `/secret/{alice_uuid}/{dataset_uuid}`
```sh
vault kv get secret/7c320c35-a681-d4ee-3339-7381dd91ac9d/dataset1
```
The output shows permission denied
```
Error reading secret/data/7c320c35-a681-d4ee-3339-7381dd91ac9d/dataset1: Error making API request.

URL: GET http://127.0.0.1:8200/v1/secret/data/7c320c35-a681-d4ee-3339-7381dd91ac9d/dataset1
Code: 403. Errors:

* 1 error occurred:
	* permission denied
```
Let's see if bob can read the secret of dataset1 shared with other users, assuming there is another user with entity_id 123456
```sh
vault kv get secret/7c320c35-a681-d4ee-3339-7381dd91ac9d/dataset1/123456
```
Still got permission denied message
```
Error reading secret/data/7c320c35-a681-d4ee-3339-7381dd91ac9d/dataset1/123456: Error making API request.

URL: GET http://127.0.0.1:8200/v1/secret/data/7c320c35-a681-d4ee-3339-7381dd91ac9d/dataset1/123456
Code: 403. Errors:

* 1 error occurred:
	* permission denied
```
# Users Grant Temporary Access to Secret Path on Vault
All the operations are done with CLI commands in this demo, which can also be performed with API calls.

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
For other auth methods, such as github, skip this step.

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
path "user-kv/data/{{identity.entity.name}}/*" {
  capabilities = [ "create", "update", "read", "delete", "list" ]
}

# For Web UI usage
path "user-kv/metadata" {
  capabilities = ["list"]
}

# Create groups
path "identity/group/name/{{identity.entity.name}}_*" {
  capabilities = [ "create", "update", "read", "delete", "list" ]
}

# Create and manage policies
path "sys/policies/acl/*" {
  capabilities = [ "create", "read", "update", "delete", "list" ]
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

## Test on Creating Groups and Adding memebers to Share Secrets
Enable key/value v2 secrets engine at path `user-kv`.
```sh
vault secrets enable -path=user-kv kv-v2
```
Log in as bob
```sh
vault login -method=userpass username="bob" password="training"
```
Write a secret to bob's secret path. He is the only user having access to it.
```sh
vault kv put user-kv/bob_smith/dataset1 secret="12344567890"
```
Log in as "alice", and try to read secret on path `user-kv/bob_smith/dataset1`
```sh
vault login -method=userpass username="alice" password="training"
vault kv get user-kv/bob_smith/dataset1
```
We can see from the output that "alice" does not have permission to the secret.
```
Error reading user-kv/data/bob_smith/dataset1: Error making API request.

URL: GET http://127.0.0.1:8200/v1/user-kv/data/bob_smith/dataset1
Code: 403. Errors:

* 1 error occurred:
	* permission denied
```
To share the secret of dataset1, Bob will create a group to share the secret. The policy of this group will be created with root or admin token on the vault server, not by the user.  
 
bob-dataset1-share-policy.hcl
```yaml
# path in <user_uuid>/<dataset_uuid> format
path "user-kv/data/bob_smith/dataset1" {
    capabilities = [ "read", "list" ]
}
```
Log in as bob
```sh
vault login -method=userpass username="bob" password="training"
```
Depoly policies
```sh
vault policy write bob-dataset1-share-policy bob-dataset1-share-policy.hcl
```

Create groups
```sh
vault write -format=json identity/group/name/bob_smith_dataset1_secret_share_group policies="bob-dataset1-share-policy"
```
Now Bob is ready to add Alice to his `bob_smith_dataset1_secret_share_group`.
```sh
vault write identity/group/name/bob_smith_dataset1_secret_share_group member_entity_ids=<alice_smith_entity_id>
```
Log in as "alice", and try to read secret on path `user-kv/bob_smith/dataset1/secret`
```sh
vault login -method=userpass username="alice" password="training"
vault kv get user-kv/bob_smith/dataset1
```
We can get the secret vaule from the output. 
```sh
====== Metadata ======
Key              Value
---              -----
created_time     2020-05-12T20:43:55.572374Z
deletion_time    n/a
destroyed        false
version          1

===== Data =====
Key       Value
---       -----
secret    12344567890

```

## Creating Group Bug Reproduce Commands (Ignore this for the demo)
There is a bug we noticed on Vault. Here are how we can reproduce it.
```sh
# login as bob
vault login -method=userpass username="bob" password="training"
# create a group named "bob_testing_group" including himself as the member
vault write -format=json identity/group name="bob_testing_group" member_entity_ids="bb7f63fd-b79a-6f13-cf79-b345247bb3c6"
```
```sh
# read the group information
vault login $VAULT_DEV_ROOT_TOKEN_ID
vault read identity/group/id/15c2ee0f-f1c0-22ff-1fe6-ca909ea866ae
```
```sh
# login as alice
vault login -method=userpass username="alice" password="training"
# create a group named "bob_testing_group" including herself as the member
vault write -format=json identity/group name="bob_testing_group" member_entity_ids="f54bb47e-0636-8a1a-1456-bcd21de5343c"
```
```sh
# read the group information
vault login $VAULT_DEV_ROOT_TOKEN_ID
vault read identity/group/id/15c2ee0f-f1c0-22ff-1fe6-ca909ea866ae
```

```sh
# login as bob
vault login -method=userpass username="bob" password="training"
# create a group named "bob_testing_group" including himself as the member
vault write -format=json identity/group name="bob_testing_group" member_entity_ids="bb7f63fd-b79a-6f13-cf79-b345247bb3c6"
```
# FRDR Encryption App

## Starting the GUI from Command Line

Navigate to the /gui folder and install required packages:

```sh
cd gui
npm install
```

To start the Electron GUI in development environment:

```sh
# Mac
NODE_ENV=development npm start

# Windows 
set NODE_ENV=development (command prompt)
$env:NODE_ENV="development" (powershell)
npm start
```

Users need to log into the key server (Hashicorp Vault) first before using the app. They need to provide the url of the key server and then login with their globus credentials. 

![login](doc/img/login.png)

You can use the app as a despostior or a requester. As a depositor, you can encrypt a dataset and grant access of the dataset's key to other users. As a requester, you can generate access request and decrypt encrypted packages downloaded from FRDR. 

### As Depositor

![encrypt](doc/img/encrypt.png)

The **Encrypt Dataset** menu option allows you to encrypt any directory on your computer by automatically generating encryption keys, encrypting them with your private key and sending them to Vault which only you have access to these encrypted dataset keys, using those keys to secure the package, and wrapping it in a metadata container called *bagit*. After clicking `Encrypt Data` you'll be prompted to the destination of encrypted package, which you can then upload to a repository such as FRDR.

![access](doc/img/grant_access.png)

The **Grant Access** menu option allows you to grant access to a package's encrypted keys on Vault to another user who has requested access. You will need the requester's ID and the package/dataset ID, both of which will normally be included in a private message sent to you along with an access request.

### As Requester

![decrypt](doc/img/decrypt.png)

The **Decrypt** menu option allows you to decrypt an encrypted package for access. Assuming you've already downloaded the package, clicking `Decrypt Data` will retrieve its encrypted dataset key from a Vault API endpoint URL (which will be normally be provided to you upon acceptance of an access request), decrypt the key with your private key (saved on your local machine) and then decrypt the package with the dataset key. You should only decrypt packages on trusted computers, as their contents may be very sensitive.
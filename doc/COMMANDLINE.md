# FRDR Encryption App

## Running from Command Line

Python 3.8 is required to run the FRDR Encryption Application from the command line. Ensure that the output of `python3 --version` shows 3.8 or higher.  

Run inside a virtual environment:
```sh
python3 -m venv env
source env/bin/activate (Mac)
. env\Scripts\activate (Windows)
```
at this point you should see (env) to the right of your command prompt, showing you that you are running inside a virtual environment.  You can now check the version of Python inside this environment:
```sh
python --version
```
And if it's indeed version 3, then install the requirements inside the virtual environment:
```sh
pip install -r requirements_mac_intel.txt (Mac with Intel processor)
pip install -r requirements_mac_silicon.txt (Mac with Apple Silicon processor)
pip install -r .\requirements_windows.txt (Windows)
```

Download and install Node.js and npm is needed: https://docs.npmjs.com/downloading-and-installing-node-js-and-npm (on a Mac you can use brew: `brew update` then `brew install node`)

Install libmagic (On a Mac: `brew install libmagic`)

To exit the virtual environment:
```sh
deactivate
```

### Troubleshooting CLI on Windows
After running `npm start` on Windows if you get an error, 
```
Error: spawn python3 ENOENT
at Process.ChildProcess._handle.onexit (node:internal/child_process:286:19)
at onErrorNT (node:internal/child_process:484:16)
at processTicksAndRejections (node:internal/process/task_queues:82:21)
```
change the code `pythonChild = require('child_process').spawn('python3', [script, port])` in `main.js` to `pythonChild = require('child_process').spawn('python', [script, port])`.

## CLI Usage

### Encryption
```sh
$ python app_cli.py encrypt \
    --vault <HashiCorp Vault address> \
    --input <path to the dir you want to encrypt> \
    --output <output path to the encrypted package> \
    --oauth
```
The output path is optional.

### Decryption
```sh
$ python app_cli.py decrypt \
    --vault <HashiCorp Vault address> \
    --input <path to the encrypted package> \
    --output <path to put the decrypted package> \
    --url <path to fetch the key saved on the key server> \
    --oauth
```
The output path is optional.

### Granting Access
```sh
$ python app_cli.py grant_access \
    --vault <HashiCorp Vault address> \
    --dataset <dataset ID> \
    --requester <vault ID of the requester> \
    --expire <date this access is going to expire>
    --frdr_api_url <FRDR API base url> \
    --oauth
```

### Show User's Vault ID
This ID is required when users create access request on FRDR.
```sh
$ python app_cli.py show_vault_id \
    --vault <HashiCorp Vault address> \
    --oauth
```

### CLI Usage Patterns
```sh
Usage:
  app_cli.py encrypt --vault=<vault_addr> (--oauth | --username=<un> --password=<pd>) --input=<ip> [--output=<op>] [--loglevel=<l>]
  app_cli.py decrypt --vault=<vault_addr> (--oauth | --username=<un> --password=<pd>) --input=<ip> --url=<key_addr> [--output=<op>] [--loglevel=<l>]
  app_cli.py grant_access --vault=<vault_addr> (--oauth | --username=<un> --password=<pd>) --dataset=<id> --requester=<id> --expire=<date> [--frdr_api_url=<url>] [--loglevel=<l>]
  app_cli.py show_vault_id --vault=<vault_addr> (--oauth | --username=<un> --password=<pd>)
  app_cli.py -h | --help

Options:
  -h --help     Show this screen.
  --username=<un>  username.
  --password=<pd>  password.
  --vault=<vault_addr>
  --input=<ip>
  --output=<op>
  --url=<key_addr>
  --dataset=<id>
  --requester=<id>
  --expire=<date>  the permission expiry date in format YYYY-mm-dd
  --frdr_api_url=<url>
  --loglevel=<l>  loglevel [default: info].
```
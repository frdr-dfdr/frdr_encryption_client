# FRDR Secure Data Desktop Client

## Getting Started

Python 3 is required to run the Radiam agent from the command line. Ensure that the output of `python3 --version` shows 3.6 or higher.  

You may want to run inside a virutal environment (see below) before running this command.
```sh
pip install -r requirements.txt
```

Run inside a virtual environment:
```sh
python3 -m venv env
source env/bin/activate
```
at this point you should see (env) to the right of your command prompt, showing you that you are running inside a virtual environment.  You can now check the version of Python inside this environment:
```sh
python --version
```
And if it's indeed version 3, then install the requirements inside the virtual environment:
```sh
pip install -r requirements.txt
```
To exit the virtual environment:
```sh
deactivate
```

## CLI Usage

To encrypt a file or a directory
```sh
$ python crypto.py -e -i <path to the file or dir you want to encrypt> 
```

To decrypt a file or a directory
```sh
$ python crypto.py -d -i <path to the encrypted file or dir> -k <path to the key>
```

Options:
```sh
  -e --encrypt  encrypt
  -d --decrypt  decrypt
  -i <input_path>, --input <input_path>  Input path 
  -o <output_path>, --output <output_path> Output path
  -k <key_path>, --key <key_path> Key path
```

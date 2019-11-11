# Deploy to Beta Server Script 🚀

This is a script to be used for both building and deploying an Ember project to a beta / test server. Included in the repo is the source code for the script, along with an executable `deploy_beta`, which you can add to your `/usr/local/bin` directory for ease of use.

# Install
There are two main ways you can *install* the script. 

1. The first and most straight forward way is to first clone this repository, then install the necessary dependencies on a user level, and finally `alias` the script for ease of use. On Mac or Linux, this would look something like:
```
$ git clone <this repo>
$ cd <this repo>
$ pip3 install --user -r requirements.txt
$ echo "alias deploy_beta='python3 /path/to/deploy_beta.py'" >> ~/.bashrc
```
  * And that's it! Fast, simple, and it should **just work** (famous last words 💀). 
  * However, if you'd prefer to run a compiled binary instead of an aliased script, you can try #2 below.

2. The second approach also begins with cloning the repository; however, the similarities pretty much stop there. Once you have cloned the repo, you then need to create a virtual environment, install all dependencies, and finally use `pyinstaller` to generate an executable binary. On Mac or Linux, this would look something like:
```
$ git clone <this repo>
$ cd <this repo>
$ python3 -m venv venv
$ pip3 install -r requirements.txt
$ pip3 install --user pyinstaller
$ <path-to-python3>/bin/pyinstaller --onefile --paths venv/lib/python3.7/site-packages:$PATH deploy_beta.py
```
  * This will create the folder `./dist` and drop an executable called `deploy_beta` in it. From there, you could then move the executable to your `bin` folder for ease of use:
```
$ mv ./dist/deploy_beta /usr/local/bin
```
  * Once that's done, you can execute the script by simply running `deploy_beta`, regardless of which folder you are in. Also, aside from `pyinstaller`, you are not required to install any other user level dependencies. 
  * The drawback to this approach however is that the executable itself can be slow to start (we're talking a few seconds on average here 😬). If this is as annoying for you as it is for me, you may want to stick with #1. 

Of course, there are also other ways to install and use the script so if you have a better / preferred method go for it. But I think the above two are the most streamlined.

# Run
Once you have the script installed, you can run it with `-h` to view the available arguments:
```
$ deploy_beta -h
usage: deploy_beta.py [-h] [-e ENV] [-b]

deploy an ember project to beta

optional arguments:
  -h, --help         show this help message and exit
  -e ENV, --env ENV  sets environment file to given file, defaults to .env
  -b, --build        calls 'ember b' to build the current ember project
```
As you can see in the output, the script allows you to specify a environment configuration file for the script to pull defined parameters from. If you do not specify your own with the `-e` argument, the script will look in the current directory for a file called `.env`. If this file does not exist, the script will fail and exit immediately. As such, before you attempt to use the script for deployment, make sure you create such a file. 

The environment variables you can set within the configuration file include:
* `REMOTE_SERVER` - **Mandatory** - The IP address / hostname of the server you want to deploy to.
* `REMOTE_PORT` - Optional - The port of the server you wan to deploy to. **Defaults** to `22`.
* `REMOTE_USER` - **Mandatory** - The username of the account on the remote server you want to deploy with.
* `REMOTE_PASSWORD` - **Mandatory** - The password of the account on the remote server you want to deploy with.
* `REMOTE_UPLOAD_DIR` - Optional - The directory on the remote server that the local folder will be uploaded to. For safety reasons, cannot be the same as `REMOTE_FINAL_DIR`. **Defaults** to `/tmp`.
* `REMOTE_FINAL_DIR` - **Mandatory** - The directory on the remote server that the local folder will be served from.
* `LOCAL_DIR` - Optional - The local directory you wish to upload to the remote server. **Defaults** to `./dist`.

Once you have a file with the appropriate variables set, you are ready to deploy! This is as easy as running something like the following:
```
$ deploy_beta -b
loading environment file ".env"...
building project...
Environment: development
[..snip..]
connecting to remote server beta.server.ly...
executing command on remote server: rm -rf ~/app/dist.bak...
executing command on remote server: mv ~/app/dist ~/app/dist.bak...
executing command on remote server: mv /tmp/dist ~/app/...
finished!
```
Running with `-b` as shown above will also build the Ember project in the current directory.

# Precautions
The script makes sure to take some precautions during the deploy process. This is so that we don't just blindly upload files to the server, overwriting everything in our way. This is achieved by breaking the deploy process up into three steps:
1. We upload the local directory to a defined upload directory on the server (defaults to `/tmp`). Note the upload directory and the final directory **cannot** be the same. If they are, the script prints an appropriate message to the user and exits immediately. Also, if the upload fails, we exit immediately and no further commands are executed on the server.
2. We delete the app's current backup directory (typically named something like `dist.bak`) from the final directory the app will be served from (`~/app` in the above example) and append `.bak` to the directory of the app itself (e.g. `~/app/dist` -> `~/app/dist.bak`), essentially creating a backup of the current app. 
3. We move the uploaded directory from its upload directory to the final directory (e.g. `/tmp/dist` -> `~/app/dist`), completing the deployment process.

Other precautions are left as an exercise to the user. In other words, be precise and deliberate in your setting of environment variables to ensure you are handling the appropriate files and directories. To an extent, like all code the script simply does what you tell it to - so don't tell it to do dangerous things!

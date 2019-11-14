# Deploy to Warply Server Script 🚀
This is a script to be used for both building and deploying an Ember project to a Warply server. Let's get started!

# Install
There are two main ways you can *install* the script. 

1. The first and most straight forward way is to first clone this repository, then install the necessary dependencies on a user level, and finally `alias` the script for ease of use. On Mac or Linux, this would look something like:
```
$ git clone <this repo>
$ cd <this repo>
$ pip3 install --user -r requirements.txt
$ echo "alias deploy='python3 /path/to/deploy.py'" >> ~/.bashrc
$ source ~/.bashrc
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
$ <path-to-python3>/bin/pyinstaller --onefile --paths venv/lib/python3.7/site-packages:$PATH deploy.py
```
  * This will create the folder `./dist` and drop an executable called `deploy` in it. From there, you could then move the executable to your `bin` folder for ease of use:
```
$ mv ./dist/deploy /usr/local/bin
```
  * Once that's done, you can execute the script by simply running `deploy`, regardless of which folder you are in. Also, aside from `pyinstaller`, you are not required to install any other user level dependencies. 
  * The drawback to this approach however is that the executable itself can be slow to start (we're talking a few seconds on average here 😬). If this is as annoying for you as it is for me, you may want to stick with #1. 

Of course, there are also other ways to install and use the script so if you have a better / preferred method go for it. But I think the above two are the most streamlined.

# Run
Once you have the script installed, you can run it with `-h` to view the available arguments:
```
usage: deploy.py [-h] [-e ENV] [-k KEY] [-bd] [-bp]

deploy an ember project

optional arguments:
  -h, --help         show this help message and exit
  -e ENV, --env ENV  sets environment file to given file, defaults to .env
  -k KEY, --key KEY  uses the defined keyfile to connect to the remote server
  -bd, --build-dev   calls 'ember b' to build the current ember project for
                     development
  -bp, --build-prod  calls 'ember b -p' to build the current ember project for
                     production
```
As you can see in the output, the script allows you to specify a environment configuration file for the script to pull defined parameters from. If you do not specify your own with the `-e` argument, the script will look in the current directory for a file called `.env`. If this file does not exist, the script will fail and exit immediately. As such, before you attempt to use the script for deployment, make sure you create such a file. 

The environment variables you can set within the configuration file include:
* `REMOTE_SERVER` - **Mandatory** - The IP address / hostname of the server you want to deploy to.
* `REMOTE_PORT` - Optional - The port of the server you wan to deploy to. **Defaults** to `22`.
* `REMOTE_USER` - **Mandatory** - The username of the account on the remote server you want to deploy with.
* `REMOTE_PASSWORD` - **Mandatory** - The password of the account on the remote server you want to deploy with. Even if you are using a key for authentication, your password is still required to execute the necessary `sudo` commands on the server.
* `REMOTE_UPLOAD_DIR` - Optional - The directory on the remote server that the local folder will be uploaded to. For safety reasons, cannot be the same as `REMOTE_FINAL_DIR`. **Defaults** to `/tmp`.
* `REMOTE_FINAL_DIR` - **Mandatory** - The directory on the remote server that the local folder will be served from.
* `LOCAL_DIR` - Optional - The local directory you wish to upload to the remote server. **Defaults** to `./dist`.

Once you have a file with the appropriate variables set, you are ready to deploy! Assuming we have a `.env` file that looks like so:
```
$ cat .env
REMOTE_SERVER='beta.server.ly'
REMOTE_USER='username'
REMOTE_PASSWORD='password'
REMOTE_FINAL_DIR='/var/www/app'
```
...deploying would look something like the following on Mac or Linux:
```
$ deploy -k ~/keys/username.pem -bd
loading environment file ".env"...
building project...
Environment: development
[..snip..]
using the following key to connect: /Users/username/keys/username.pem
connecting to remote server beta.server.ly...
uploading...
local directory dist uploaded succesfully...
executing command on remote server: sudo -S -p '' rm -rf /var/www/app/dist.bak...
executing command on remote server: sudo -S -p '' mv /var/www/app/dist /var/www/app/dist.bak...
executing command on remote server: sudo -S -p '' mv /tmp/dist var/www/app/...
finished!
```
At this point you might be wondering why we need to declare both a `REMOTE_UPLOAD_DIR` and `REMOTE_FINAL_DIR` 🤔. If so, read the precautions section below!

# Precautions
The script makes sure to take some precautions during the deploy process. This is so that we don't just blindly upload files to the server, overwriting everything in our way. This is achieved by breaking the deploy process up into three steps:
1. We upload the local directory to a defined upload directory on the server (defaults to `/tmp`). Note the upload directory and the final directory **cannot** be the same. If they are, the script prints an appropriate message to the user and exits immediately. Also, if the upload fails, we exit immediately and no further commands are executed on the server.
2. We delete the app's current backup directory (typically named something like `dist.bak`) from the final directory the app will be served from (`~/app` in the above example) and append `.bak` to the directory of the app itself (e.g. `~/app/dist` -> `~/app/dist.bak`), essentially creating a backup of the current app. 
3. We move the uploaded directory from its upload directory to the final directory (e.g. `/tmp/dist` -> `~/app/dist`), completing the deployment process.

Other precautions are left as an exercise to the user. In other words, be precise and deliberate in your setting of environment variables to ensure you are handling the appropriate files and directories. To an extent, like all code the script simply does what you tell it to - so don't tell it to do dangerous things!

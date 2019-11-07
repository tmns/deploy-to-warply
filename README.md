# Deploy to Beta Server Script 🚀

This is a script to be used for both building and deploying an Ember project to a beta / test server. Included in the repo is the source code for the script, along with an executable `deploy_beta`, which you can add to your `/usr/local/bin` directory for ease of use.

# Install
There are two main ways you can *install* the script. 

1. The first and most straight forward way is to download the latest pre-built binary from the releases page [here](). Once you have downloaded the binary, you can make it executable and move it to your `bin` folder (to make it globally callable) like so:
```
$ chmod +x ~/Downloads/deploy_beta
$ mv ~/Downloads/deploy_beta /usr/local/bin
```
* That's it! No installation of dependencies. No other BS. Just download the binary, make it executable, and execute it. 
* The drawback to this however is that it can be slow to start (we're talking a few seconds on average here 😬). If this is as annoying for you as it is for me, you may consider going with option #2 below. 

2. The second way to *install* the script is to download its source code and `requirements.txt` file, install its dependencies on a user level, and create an `alias` for easy access. This would look something like this:
```
$ git clone <this repo>
$ cd <this repo>
$ pip3 install --user -r requirements.txt
$ echo "alias deploy_beta='python3 /path/to/deploy_beta.py'" >> ~/.bashrc
```
* And that's it once again! Not so bad either in my opinion and it should **just work** (famous last words 💀).

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
1. We upload the local directory to a defined upload directory on the server (defaults to `/tmp`). Note the upload directory and the final directory **cannot** be the same. If they are, the script prints an appropriate message to the user and exits immediately.
2. We delete the app's current backup directory (typically named something like `dist.bak`) from the final directory the app will be served from (`~/app` in the above example) and append `.bak` to the directory of the app itself (e.g. `~/app/dist` -> `~/app/dist.bak`), essentially creating a backup of the current app. 
3. We move the uploaded directory from its upload directory to the final directory (e.g. `/tmp/dist` -> `~/app/dist`), completing the deployment process.

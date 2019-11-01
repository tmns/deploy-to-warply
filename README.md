# Deploy to Beta Server Script 🚀

This is a script to be used for both building and deploying an Ember project to the Warply beta / test server (beta.warp.ly). Included in the repo is the source code for the script, along with an executable `deploy_beta`, which you can add to your `/usr/local/bin` directory for ease of use.

# Install
There are two main ways you can *install* the script. The first and most straight forward way is to download the latest pre-built binary from the releases page [here](). Once you have downloaded the binary, you can make it executable and move it to your `bin` folder (to make it globally callable) like so:
```
$ chmod +x ~/Downloads/deploy_beta
$ mv ~/Downloads/deploy_beta /usr/local/bin
```
That's it! No installation of dependencies. No other BS. Just download the binary, make it executable, and execute it. The drawback to this however is that it can be slow to start (we're talking a few seconds on average here 😬). If this is as annoying for you as it is for me, you may consider the following alternative.

The second way to *install* the script is to download its source code and `requirements.txt` file, install its dependencies on a user level, and create an `alias` for easy access. This would look something like this:
```
$ git clone <this repo>
$ cd <this repo>
$ pip3 install --user -r requirements.txt
$ echo "alias deploy_beta='python3 /path/to/deploy_beta.py'" >> ~/.bashrc
```
And that's it once again! Not so bad either in my opinion and it should **just work** (famous last words 💀).

Of course, there are also other ways to install and use the script so if you have a better / preferred method go for it. But I think the above two are the most streamlined.

# Run

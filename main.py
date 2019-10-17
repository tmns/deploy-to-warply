import os
from config import Config
from client import Client


def main():
    client = Client(Config)
    client.execute(f'mkdir {Config.remote_dir}')
    local_dir = os.walk(os.path.abspath(Config.local_dir))
    for root, dirs, files in local_dir:
        for file in files:
            local_file = root + '/' + file
            client.upload(local_file, Config.remote_dir)
            filename = file.split('/')[-1]
            print(f'Uploaded {filename} to {Config.remote_server}:{Config.remote_dir}.')
    client.execute("rm -rf /tmp/test/dist.bak")
    client.execute("mv /tmp/test/dist /tmp/test/dist.bak")
    client.execute("mv /tmp/dist /tmp/test")
    client.disconnect()
    print('finished!')

main()

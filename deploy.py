import os, sys, subprocess, argparse
from os import environ
from dotenv import find_dotenv, load_dotenv
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException
from scp import SCPClient, SCPException
from io import StringIO


class Config:
    def __init__(self, env):
        print(f'loading environment file "{env}"...')
        if not os.path.exists(env):
            print(
                f'given environment file "{env}" does not exist\nexiting...')
            sys.exit()
        load_dotenv(dotenv_path=env, verbose=True)
        
        self.remote_server = environ.get('REMOTE_SERVER')
        self.remote_port = environ.get('REMOTE_PORT') or 22
        self.remote_user = environ.get('REMOTE_USER')
        self.remote_password = environ.get('REMOTE_PASSWORD') or None
        self.remote_upload_dir = environ.get('REMOTE_UPLOAD_DIR') or '/tmp'
        self.remote_final_dir = environ.get('REMOTE_FINAL_DIR')
        self.local_dir = environ.get('LOCAL_DIR') or 'dist'


class Client:
    def __init__(self, config):
        self.remote_server = config.remote_server
        self.remote_port = config.remote_port
        self.remote_user = config.remote_user
        self.remote_password = config.remote_password
        self.client = None

    def __connect(self, key=None):
        if self.client is None:
            try:
                print(f'connecting to remote server {self.remote_server}...')
                client = SSHClient()
                client.load_system_host_keys()
                client.set_missing_host_key_policy(AutoAddPolicy())
                if key is not None:
                    client.connect(hostname=self.remote_server, port=self.remote_port, 
                                   username=self.remote_user, pkey=key)
                else:
                    client.connect(self.remote_server, self.remote_port,
                                   self.remote_user, self.remote_password)
            except Exception as ex:
                print(ex)
            finally:
                return client
        return self.client

    def disconnect(self):
        self.client.close()

    def execute(self, cmd):
        """Executes a single command on the remote server."""
        if self.client is None:
            self.client = self.__connect()
        print(f'executing command on remote server: {cmd}...')
        stdin, stdout, stderr = self.client.exec_command(cmd)
        return stdout.readlines()

    def upload(self, local_dir, remote_upload_dir, key=None):
        """Uploads a local directory to the remote server."""
        if self.client is None:
            self.client = self.__connect(key)
        scp = SCPClient(self.client.get_transport(), progress=self.__progress)
        try:
            scp.put(local_dir,
                    recursive=True,
                    remote_path=remote_upload_dir)
        except SCPException:
            raise SystemExit(SCPException.message)
        finally:
            scp.close()

    def __progress(self, filename, size, sent):
        """Displays SCP progress."""
        sys.stdout.write(
            f'uploading {filename}: {float(sent) / float(size) * 100:.2f}%    \r')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="deploy an ember project to beta")
    parser.add_argument(
        "-e", "--env", help="sets environment file to given file, defaults to .env", default=".env")
    parser.add_argument(
        "-k", "--key", help="uses the defined keyfile to connect to the remote server")
    parser.add_argument(
        "-bd", "--build-dev", help="calls 'ember b' to build the current ember project for development", action="store_true")
    parser.add_argument(
        "-bp", "--build-prod", help="calls 'ember b -p' to build the current ember project for production", action="store_true")
    args = parser.parse_args()

    config = Config(args.env)
    print(args)

    if args.build_dev:
        print('building project for development...')
        try:
            subprocess.run(["ember", "b"], check=True)
        except Exception as ex:
            sys.exit()
    elif args.build_prod:
        print('building project for production...')
        try:
            subprocess.run(["ember", "b", "-p"])
        except Exception as ex:
            sys.exit()

    key = None
    if args.key:
        print(f'using the following key to connect: {args.key}')
        try:
            key = RSAKey.from_private_key_file(args.key)
        except Exception as ex:
            print(f'The following exception occurred when attempting to load the given key:\n{ex}')
            sys.exit()

    local_dir = config.local_dir
    remote_upload_dir = config.remote_upload_dir
    remote_final_dir = config.remote_final_dir
    if remote_upload_dir == remote_final_dir:
        print('REMOTE_UPLOAD_DIR and REMOTE_FINAL_DIR cannot be the same!\nexiting...')
        sys.exit()

    client = Client(config)

    client.upload(local_dir, remote_upload_dir, key)
    client.execute(f'rm -rf {remote_final_dir}/{local_dir}.bak')
    client.execute(
        f'mv {remote_final_dir}/{local_dir} {remote_final_dir}/{local_dir}.bak')
    client.execute(f'mv {remote_upload_dir}/{local_dir} {remote_final_dir}')

    client.disconnect()
    print('finished!')
import os
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException
from scp import SCPClient, SCPException 
from io import StringIO
from config import Config


class Client:
    def __init__(self, config):
        self.remote_server = config.remote_server
        self.remote_port = config.remote_port
        self.remote_user = config.remote_user
        self.remote_password = config.remote_password
        self.remote_dir = config.remote_dir
        self.client = None

    def __connect(self):
        if self.client is None:
            try:
                print(f'connecting to remote server {self.remote_server}...')
                client = SSHClient()
                client.load_system_host_keys()
                client.set_missing_host_key_policy(AutoAddPolicy())
                client.connect(self.remote_server, self.remote_port, self.remote_user, self.remote_password)
            except Exception as ex:
                print(ex)
            finally:
                return client
        return self.client

    def disconnect(self):
        """Close ssh connection."""
        self.client.close()

    def execute(self, cmd):
        """Executes a single unix command."""
        if self.client is None:
            self.client = self.__connect()
        print(f'executing command on remote server {cmd}...')
        stdin, stdout, stderr = self.client.exec_command(cmd)
        return stdout.readlines()

    def upload(self, file, remote_directory):
        """Upload a single file to a remote directory."""
        if self.client is None:
            self.client = self.__connect()
        scp = SCPClient(self.client.get_transport())
        try:
            scp.put(file,
                    recursive=True,
                    remote_path=remote_directory)
        except SCPException:
            raise SCPException.message
        finally:
            scp.close()


if __name__ == '__main__':
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


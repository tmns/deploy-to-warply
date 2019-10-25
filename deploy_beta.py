import sys
from os import environ
from dotenv import load_dotenv
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException
from scp import SCPClient, SCPException 
from io import StringIO


load_dotenv(verbose=True)

class Config:
    remote_server = environ.get('REMOTE_SERVER')
    remote_port = environ.get('REMOTE_PORT') or 22
    remote_user = environ.get('REMOTE_USER')
    remote_password = environ.get('REMOTE_PASSWORD')
    remote_upload_dir = environ.get('REMOTE_UPLOAD_DIR') or '/tmp'
    remote_final_dir = environ.get('REMOTE_FINAL_DIR')
    local_dir = environ.get('LOCAL_DIR')


class Client:
    def __init__(self, config):
        self.remote_server = config.remote_server
        self.remote_port = config.remote_port
        self.remote_user = config.remote_user
        self.remote_password = config.remote_password
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
        print(f'executing command on remote server: {cmd}...')
        stdin, stdout, stderr = self.client.exec_command(cmd)
        return stdout.readlines()

    def upload(self, local_dir, remote_upload_dir):
        """Upload a single file to a remote directory."""
        if self.client is None:
            self.client = self.__connect()
        print(f'uploading {local_dir} to {Config.remote_server}:{remote_upload_dir}...')
        scp = SCPClient(self.client.get_transport(), progress=self.__progress)
        try:
            scp.put(local_dir,
                    recursive=True,
                    remote_path=remote_upload_dir)
        except SCPException:
            raise SCPException.message
        finally:
            scp.close()

    def __progress(self, filename, size, sent):
        """Display SCP progress."""
        sys.stdout.write(f'uploading {filename}: {float(sent) / float(size) * 100:.2f}%    \r')


if __name__ == '__main__':
    local_dir = Config.local_dir
    remote_upload_dir = Config.remote_upload_dir
    remote_final_dir = Config.remote_final_dir
    client = Client(Config)
    client.upload(local_dir, remote_upload_dir)
    client.execute(f'rm -rf {remote_final_dir}/{local_dir}.bak')
    client.execute(f'mv {remote_final_dir}/{local_dir} {remote_final_dir}/{local_dir}.bak')
    client.execute(f'mv {remote_upload_dir}/{local_dir} {remote_final_dir}')
    client.disconnect()
    print('finished!')


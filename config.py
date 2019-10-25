from os import environ
from dotenv import load_dotenv

load_dotenv(verbose=True)

class Config:
    remote_server = environ.get('REMOTE_SERVER')
    remote_port = environ.get('REMOTE_PORT')
    remote_user = environ.get('REMOTE_USER')
    remote_password = environ.get('REMOTE_PASSWORD')
    remote_upload_dir = environ.get('REMOTE_UPLOAD_DIR')
    remote_final_dir = environ.get('REMOTE_FINAL_DIR')
    local_dir = environ.get('LOCAL_DIR')

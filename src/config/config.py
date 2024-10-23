import os, io
from cryptography.fernet import Fernet
from dotenv import dotenv_values, load_dotenv

class APPConfig:
    def __init__(self):
        self._envs = self._load_envs()
        self.BIZOPS_HOST          = self._envs.get("BIZOPS_HOST")
        self.BIZOPS_DB_USER       = self._envs.get("BIZOPS_DB_USER")
        self.BIZOPS_DB_PASSWORD   = self._envs.get("BIZOPS_DB_PASSWORD")
        self.OPS_MAIL             = self._envs.get("OPS_MAIL")
        self.OPS_MAIL_PASSWORD    = self._envs.get("OPS_MAIL_PASSWORD")
        self.S3_ACCESS_KEY_ID     = self._envs.get("S3_ACCESS_KEY_ID")  
        self.S3_SECRET_ACCESS_KEY = self._envs.get("S3_SECRET_ACCESS_KEY")
        self.RESOURCE_KEY         = self._envs.get('RESOURCE_KEY', '')

    def _load_envs(self) -> dict:
        try:
            cipher = Fernet(os.environ.get('RESOURCE_KEY').encode())
        except:
            load_dotenv('src/config/creds.env')
            resource_key = os.getenv("RESOURCE_KEY")  
            cipher = Fernet(resource_key)

        with open('src/config/creds.enc', 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = cipher.decrypt(encrypted_data)
        decrypted_file = io.StringIO(decrypted_data.decode())
        return dotenv_values(stream=decrypted_file)


ap = APPConfig()
ap._load_envs()

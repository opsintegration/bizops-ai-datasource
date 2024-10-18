import os
from dotenv import load_dotenv

load_dotenv('creds.env')
bizops_host       = os.getenv("BIZOPS_HOST")
bizops_user       = os.getenv("BIZOPS_DB_USER")
bizops_password   = os.getenv("BIZOPS_DB_PASSWORD")
ops_mail          = os.getenv("OPS_MAIL")
ops_mail_password = os.getenv("OPS_MAIL_PASSWORD")
s3_access_key_id  = os.getenv("S3_ACCESS_KEY_ID")  
s3_secret_access_key = os.getenv("S3_SECRET_ACCESS_KEY")

DATA_BASE_CONFIG = {
    'bizops': {
        'bizops_host'       : bizops_host,
        'bizops_user'       : bizops_user,
        'bizops_password'   : bizops_password,
        'ops_mail'          : ops_mail,
        'ops_mail_password' : ops_mail_password,
        's3_access_key_id'      : s3_access_key_id,
        's3_secret_access_key'  : s3_secret_access_key,
    },
}
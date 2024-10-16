import os
from dotenv import load_dotenv

load_dotenv('creds.env')
bizops_host       = os.getenv("BIZOPS_HOST")
bizops_user       = os.getenv("BIZOPS_DB_USER")
bizops_password   = os.getenv("BIZOPS_DB_PASSWORD")
ops_mail          = os.getenv("OPS_MAIL")
ops_mail_password = os.getenv("OPS_MAIL_PASSWORD")

DATA_BASE_CONFIG = {
    'bizops': {
        'bizops_host'       : bizops_host,
        'bizops_user'       : bizops_user,
        'bizops_password'   : bizops_password,
        'ops_mail'          : ops_mail,
        'ops_mail_password' : ops_mail_password,
    },
}
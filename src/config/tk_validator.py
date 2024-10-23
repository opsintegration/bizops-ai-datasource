from flask import request, abort
from src.config.config import APPConfig

class Token():
    def __init__(self):
        self.app_config       = APPConfig()
        self.data_tools_token = self.app_config.DATA_TOOLS_TOKEN    

    def __key(self):
        return self.data_tools_token
    
    def key(self):
        key = self.__key()
        return key
    
    def check_token(self):
        token = request.headers.get('Authorization')
        if not token or token.split()[0] != 'Bearer' \
            or token.split()[1] != self.key():
            abort(401, 'Unauthorized')
import psycopg2
from psycopg2 import Error
from repository.params import DATA_BASE_CONFIG

bizops_host       = DATA_BASE_CONFIG["bizops"]["bizops_host"]
bizops_user       = DATA_BASE_CONFIG["bizops"]["bizops_user"]
bizops_password   = DATA_BASE_CONFIG["bizops"]["bizops_password"]
ops_mail          = DATA_BASE_CONFIG["bizops"]["ops_mail"]
ops_mail_password = DATA_BASE_CONFIG["bizops"]["ops_mail_password"]

class Database():
    def __init__(self, connection_name):
        self.connection_name    = connection_name
        self.bizops_host        = bizops_host       
        self.bizops_user        = bizops_user       
        self.bizops_password    = bizops_password   

    def connect_open(self):
        try:
            self.conn = psycopg2.connect(host=self.bizops_host, user=self.bizops_user, password=self.bizops_password)            
            self.cur = self.conn.cursor()
            return "OK"
        except Error as e: return ("Database connection failure!! Check error:", e)
        
    def execute_QUERY(self, query):        
        self.connect_open()
        self.cur.execute(query)
        result = self.cur.fetchall()
        self.disconnect()
        return result
    
    def execute(self, query): 
        self.cur.execute(query)

    def commit(self):         
        self.conn.commit()

    def disconnect(self):     
        self.conn.close()

    def query_commit(self, query):
        if self.connect_open() == "OK":                
            self.execute(query)
            self.commit()
            self.disconnect()
        else:
            print("...CONNECTION FAILURE...")      

    def query_result(self, query):
        if self.connect_open() == "OK":
            result = self.execute_QUERY(query)
            return result[0][0] if result else None
        else:
            print("...CONNECTION FAILURE...")          

    def query_result_list(self, query):
        if self.connect_open() == "OK":
            result = self.execute_QUERY(query)
            return result
        else:
            print("...CONNECTION FAILURE...")      
import psycopg2
import logging
from config.config import APPConfig

log = logging.getLogger('database')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

class Database():
    def __init__(self, connection_name):
        self.app_config      = APPConfig()
        self.bizops_host     = self.app_config.BIZOPS_HOST         
        self.bizops_user     = self.app_config.BIZOPS_DB_USER      
        self.bizops_password = self.app_config.BIZOPS_DB_PASSWORD  
        self.connection_name = connection_name
        self.conn            = None
        self.cur             = None

    def connect_open(self):
        try:
            log.debug("Connecting to database at %s with user %s", self.bizops_host, self.bizops_user)
            self.conn = psycopg2.connect(
                host=self.bizops_host,
                user=self.bizops_user,
                password=self.bizops_password,
                port=5432
            )
            self.cur = self.conn.cursor()
        except psycopg2.OperationalError as e:
            log.error("Operational error: %s", e)
            self.cur = None  # Ensure `cur` is set to None on failure
        except Exception as e:
            log.error("Failed to connect to the database: %s", e)
            self.cur = None  # Ensure `cur` is set to None on failure

    def execute_QUERY(self, query):
        self.connect_open()
        if self.cur is None:
            log.error("Cannot execute query, cursor is not initialized.")
            return None  # Or handle the error as needed
        
        try:
            self.cur.execute(query)
            result = self.cur.fetchall()
        except Exception as e:
            log.error("Query execution failed: %s", e)
            result = None  # Handle the error as needed
        finally:
            self.disconnect()
        
        return result

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def query_result_list(self, query):
        result = self.execute_QUERY(query)
        return result

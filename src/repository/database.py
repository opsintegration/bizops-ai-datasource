import psycopg2
import logging
from psycopg2 import Error
from repository.params import DATA_BASE_CONFIG

log = logging.getLogger('database')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

bizops_host = DATA_BASE_CONFIG["bizops"]["bizops_host"]
bizops_user = DATA_BASE_CONFIG["bizops"]["bizops_user"]
bizops_password = DATA_BASE_CONFIG["bizops"]["bizops_password"]

class Database():
    def __init__(self, connection_name):
        self.connection_name = connection_name
        self.bizops_host = bizops_host
        self.bizops_user = bizops_user
        self.bizops_password = bizops_password
        self.conn = None
        self.cur = None

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

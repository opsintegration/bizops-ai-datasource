from sqlalchemy import create_engine
from playwright.sync_api import sync_playwright
from repository.database import Database
import time, os, boto3, logging
from config.config import APPConfig

log = logging.getLogger('data_processing')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

class PageController():
    def __init__(self):
        self.app_config = APPConfig()
        self.bizops_host          = self.app_config.BIZOPS_HOST         
        self.bizops_user          = self.app_config.BIZOPS_DB_USER      
        self.bizops_password      = self.app_config.BIZOPS_DB_PASSWORD  
        self.ops_mail             = self.app_config.OPS_MAIL            
        self.ops_mail_password    = self.app_config.OPS_MAIL_PASSWORD   
        self.s3_access_key_id     = self.app_config.S3_ACCESS_KEY_ID    
        self.s3_secret_access_key = self.app_config.S3_SECRET_ACCESS_KEY        
        self.engine = create_engine(f'postgresql+psycopg2://{self.bizops_user}:{self.bizops_password}@{self.bizops_host}/bizops')
        self.download_dir = os.path.join(os.getcwd(), 'src', 'downloads')
        self.bucket_name = 'bizops-ai'
        
    def __close_browser(self, browser, playwright):
        try:
            if browser: browser.close()
            if playwright: playwright.stop()
        except Exception as e: log.info(f".... Error during cleanup: {e}")

    def __start_driver(self):
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        return page, browser, playwright

    def __login_google_sites(self):
        url = 'https://sites.google.com/u/0/new?pli=1&authuser=0&tgif=d'
        page, browser, playwright = self.__start_driver()
        try:
            page.goto(url, timeout=60000)
            time.sleep(3)

            log.info('.... Entering username')
            page.wait_for_selector('//*[@id="identifierId"]', timeout=30000).fill(self.ops_mail)

            log.info('.... Click Next after entering username')
            page.click('//*[@id="identifierNext"]')
            time.sleep(3)

            log.info('.... Entering password')
            page.wait_for_selector('//*[@id="password"]', timeout=10000).fill(self.ops_mail_password)

            log.info('.... Click Next after entering password')
            page.click('//*[@id="passwordNext"]')
            time.sleep(5)
            # page.screenshot(path=os.path.join(self.download_dir, 'screenshot.png'), full_page=True)                    
            return page, browser, playwright
        except Exception as e:
            log.info(f"An error occurred: {e}")
        
    def __download_page_as_pdf(self, description, page, url, has_dropdown):
        try: 
            log.info(f'...... Processing page to pdf and downloading: {description} ')
            page.goto(url, timeout=60000)
            time.sleep(3)
            
            if has_dropdown:
                query = f"SELECT description, url, button_path FROM ai.page_dropdown_mapping WHERE url = '{url}' order by id asc;"
                db = Database('bizops')
                dropdowns = db.query_result_list(query)

                for dropdown in dropdowns:
                    button_path = dropdown[2]
                    time.sleep(2)                    
                    try:
                        page.wait_for_selector(button_path, timeout=10000)
                        page.click(button_path)
                        page.wait_for_timeout(3000)                        
                        time.sleep(2)                
                    except Exception as e:
                        log.info(f"Error clicking dropdown {button_path} : {e}")         
                
            page.pdf(path=os.path.join(self.download_dir, f'{description}.pdf'))
            time.sleep(3)
        except Exception as e:
            log.info(f"An error occurred: {e}")    

    # def __download_page_as_html(self, description, page, url):
    #     log.info(f'...... Processing page to pdf and downloading: {description} ')
    #     try:
    #         download_dir = self.download_dir
    #         file_name = 'downloaded_page.html'
    #         file_path = os.path.join(download_dir, file_name)

    #         page.goto(url, timeout=60000)
    #         time.sleep(3)
    #         page.wait_for_load_state("networkidle")
            
    #         with open(file_path, 'w', encoding='utf-8') as file_handle:
    #             file_handle.write(page.content())
    #         time.sleep(3)
    #         log.info(f".... File downloaded: {file_path}")

    #     except Exception as e:
    #         log.info(f"Error clicking dropdown: {e}")
    
    def __process_google_sites_doc(self, theme_id:int = None):

        query = 'select id, theme_id, description, url, updated_date, has_dropdown from ai.page_control'
        if theme_id: 
            query = f'{query} where theme_id = {theme_id} and'
        elif not theme_id: 
            query = f'{query} where'
        query = f'{query} active is true order by id asc;'
        db = Database('bizops')
        pages_list = db.query_result_list(query)              

        if len(pages_list) > 0:
            page, browser, playwright = self.__login_google_sites()
            if page:
                for single_page in pages_list:
                    theme_id     = single_page[1]
                    description  = single_page[2]
                    url          = single_page[3]
                    has_dropdown = single_page[5]

                    self.__download_page_as_pdf(description, page, url, has_dropdown)
                    # self.__download_page_as_html(description, page, url)

            if browser and playwright:
                self.__close_browser(browser, playwright)
                log.info(".... Browser and Playwright closed successfully.")

    def __list_files_and_send_to_s3(self):
        folder_path = self.download_dir
        try:
            files = os.listdir(folder_path)

            for file in files:
                file_name, file_extension = os.path.splitext(file)
                file_name = file_name.lower()
                doc_name = self.__get_file_name(file_name)

                log.info(f'........ Sending {doc_name} to s3 folder: {file_name}')
                self.__send_files_to_s3(file_name, file_extension, doc_name)
                
        except FileNotFoundError:
            log.info(f"Folder '{folder_path}' not found.")

    def __clean_local_files(self):
        folder_path = self.download_dir
        try:
            files = os.listdir(folder_path)
            log.info(f'.... Listing files: \n   {files}')

            for file in files:
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    log.info(f"Deleted: {file_path}")

        except FileNotFoundError:
            log.info(f"Folder '{folder_path}' not found.")

    def __format_file_name(self, file_name: str) -> str:
        try:
            formatted_name = file_name.replace(' ', '_').lower()
            return formatted_name
        except AttributeError as e:
            log.info(f"Error formatting file name: {e} - Ensure that file_name is a string.")
        except Exception as e:
            log.info(f"An unexpected error occurred: {e}")

    def __get_file_name(self, description):
        query = f"SELECT DISTINCT pt.description FROM ai.page_theme pt JOIN ai.page_control pc ON pt.id = pc.theme_id WHERE LOWER(pc.description) = LOWER('{description}');"
        db = Database('bizops')
        try:
            result = db.query_result_list(query)
            if result:
                file_name = result[0][0]
                formatted_file_name = self.__format_file_name(file_name)
                return formatted_file_name
            else:
                raise ValueError(f"No result found for description: {description}")
        except (IndexError, ValueError) as e:
            log.info(f"Error retrieving file name: {e}")
        except Exception as e:
            log.info(f"An unexpected error occurred: {e}")

    def __send_files_to_s3(self, file_name, file_extension, doc_name, retries=5, wait_time=10):
        folder_path = self.download_dir
        file_name = file_name + file_extension
        s3_file_path = os.path.join(folder_path, file_name)
        attempt = 0

        while not os.path.exists(s3_file_path) and attempt < retries:
            log.info(f"........ Waiting for file {file_name} to appear .... attempt {attempt + 1}/{retries}")
            time.sleep(wait_time)
            attempt += 1

        if not os.path.exists(s3_file_path):
            raise FileNotFoundError(f"........ File '{file_name}' not found in folder '{folder_path}'")
        
        try:
            s3_client = boto3.client('s3', aws_access_key_id=self.s3_access_key_id, aws_secret_access_key=self.s3_secret_access_key)
            with open(s3_file_path, 'rb') as f:
                s3_key = f'{doc_name}/{file_name}'
                s3_client.upload_fileobj(f, self.bucket_name, s3_key)
            log.info(f"........ File '{s3_file_path}' uploaded to S3 bucket under '{s3_key}'")

        except Exception as e:
            raise Exception(f"Error sending file to AWS S3: {e}")

    def process_google_sites_doc(self, theme_id:int = None):
        self.__process_google_sites_doc(theme_id)            

    def process_file_to_storage(self):        
        self.__list_files_and_send_to_s3()
        
    def clean_local_files(self):
        self.__clean_local_files()



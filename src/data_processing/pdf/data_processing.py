from repository.params import DATA_BASE_CONFIG
from sqlalchemy import create_engine
from playwright.sync_api import sync_playwright
from repository.database import Database
import time, os

bizops_host       = DATA_BASE_CONFIG["bizops"]["bizops_host"]
bizops_user       = DATA_BASE_CONFIG["bizops"]["bizops_user"]
bizops_password   = DATA_BASE_CONFIG["bizops"]["bizops_password"]
ops_mail          = DATA_BASE_CONFIG["bizops"]["ops_mail"]
ops_mail_password = DATA_BASE_CONFIG["bizops"]["ops_mail_password"]

class PageController():
    def __init__(self):
        self.bizops_host        = bizops_host       
        self.bizops_user        = bizops_user       
        self.bizops_password    = bizops_password   
        self.ops_mail           = ops_mail          
        self.ops_mail_password  = ops_mail_password 
        self.engine = create_engine(f'postgresql+psycopg2://{self.bizops_user}:{self.bizops_password}@{self.bizops_host}/bizops')
        self.download_dir      = os.path.join(os.getcwd(), 'repository', 'downloads')
        
    def __close_browser(self, browser, playwright):
        try:
            if browser: browser.close()
            if playwright: playwright.stop()
        except Exception as e: print(f"Error during cleanup: {e}")

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

            print('##### Entering username')
            page.wait_for_selector('//*[@id="identifierId"]', timeout=30000).fill(self.ops_mail)

            print('##### Click Next after entering username')
            page.click('//*[@id="identifierNext"]')
            time.sleep(3)

            print('##### Entering password')
            page.wait_for_selector('//*[@id="password"]', timeout=10000).fill(self.ops_mail_password)

            print('##### Click Next after entering password')
            page.click('//*[@id="passwordNext"]')
            time.sleep(5)
            # page.screenshot(path=os.path.join(self.download_dir, 'screenshot.png'), full_page=True)                    
            return page, browser, playwright
        except Exception as e:
            print(f"An error occurred: {e}")
        
    def __download_page_as_pdf(self, description, page, url, has_dropdown):
        try: 
            page.goto(url, timeout=60000)
            time.sleep(5)
            
            if has_dropdown:
                query = f"SELECT description, url, button_path FROM ai.page_dropdown_mapping WHERE url = '{url}';"
                db = Database('bizops')
                dropdowns = db.query_result_list(query)

                for dropdown in dropdowns:
                    button_path = dropdown[2]
                    try:
                        page.wait_for_selector(button_path, timeout=10000).click()
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f"Error clicking dropdown: {e}")

            page.pdf(path=os.path.join(self.download_dir, f'{description}.pdf'))
            time.sleep(5)
            # page.screenshot(path=os.path.join(self.download_dir, f'{description}.png'), full_page=True)

        except Exception as e:
            print(f"An error occurred: {e}")            

    
    def process_pages(self, theme_id:int = None):
        query = 'select id, theme_id, description, url, updated_date, has_dropdown from ai.page_control'
        if theme_id: query = f'{query} where theme_id = {theme_id}'

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
                    
                    print(f'.... Processing page: {description}')                                                         
                    self.__download_page_as_pdf(description, page, url, has_dropdown)


            if browser and playwright:
                self.__close_browser(browser, playwright)
                print("##### Browser and Playwright closed successfully.")    

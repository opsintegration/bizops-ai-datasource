from data_processing.pdf.data_processing import PageController
from data_processing.email_alerts import EmailController
import traceback, logging

log = logging.getLogger('main')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

def run_process():
    try:
        ai = PageController()
        
        log.info("Starting Google Sites document processing...")
        ai.process_google_sites_doc()
        
        log.info("Processing file to storage...")
        ai.process_file_to_storage()
        
        log.info("Cleaning local files...")
        ai.clean_local_files()
        
        log.info("Process completed successfully.")

    except Exception as e:
        error_message = f"Docs Source For AI Job Error:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        log.info(error_message)
        pc = EmailController()
        
        pc.send_error_email(subject="AI DOCS SOURCE JOB - Integration Errors Warning", body=error_message)

if __name__ == "__main__":
    run_process()
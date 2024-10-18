from data_processing.pdf.data_processing import PageController
        
ai = PageController()

ai.scrap_datasource()

ai.process_file_to_storage()

ai.clean_local_files()
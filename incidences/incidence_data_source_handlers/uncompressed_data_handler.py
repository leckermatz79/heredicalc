# V3/incidences/incidence_data_source_handlers/uncompressed_data_handler.py
import logging
from V3.incidences.incidence_data_source_handlers.data_source_handler import DataSourceHandler

class UncompressedDataHandler(DataSourceHandler):
    """Handler for uncompressed file datasets."""

    def download_and_extract(self):
        """
        Downloads an uncompressed file directly into the data directory.
        
        Since the data is uncompressed, no extraction is required.
        """
        file_path = self.download_file()  # Download the file
        self.log_download_timestamp()
        logging.info(f"File saved as {file_path}, no extraction required.")
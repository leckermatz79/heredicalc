# incidences/incidence_data_source_handlers/zip_data_handler.py
import os
import logging
import zipfile
from .data_source_handler import DataSourceHandler

class ZipDataHandler(DataSourceHandler):
    """Handler for ZIP file datasets."""

    def __init__(self, source_config, base_data_dir=None, force_download=False):
        super().__init__(source_config, base_data_dir=base_data_dir, force_download=force_download)

    def download_and_extract(self):
        """
        Downloads and extracts the ZIP data file.
        
        The ZIP file is downloaded, extracted into the data directory,
        and the original ZIP file is removed afterward.
        """
        zip_path = self.download_file()  # Download the ZIP file to the specified path

        # Extract the contents of the ZIP file to the data directory
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(self.data_dir)
        os.remove(zip_path)  # Remove the ZIP file after extraction
        
        logging.info(f"Data extracted to {self.data_dir}")
        self.log_download_timestamp()
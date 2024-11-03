# V3/incidences/incidence_data_source_handlers/csv_data_handler.py
import logging
from .data_source_handler import DataSourceHandler

class CsvDataHandler(DataSourceHandler):
    """Handler for uncompressed file datasets."""
    
    def __init__(self, source_config, base_data_dir=None, force_download=False):
        super().__init__(source_config, base_data_dir=base_data_dir, force_download=force_download)

    def download_and_extract(self):
        """
        Downloads an uncompressed file directly into the data directory.
        Since CSV is an uncompressed format, no download is necessary.
        """
        pass
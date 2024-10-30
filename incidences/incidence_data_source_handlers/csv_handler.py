# V3/incidences/incidence_data_source_handlers/csv_data_handler.py
import logging
from V3.incidences.incidence_data_source_handlers.data_source_handler import DataSourceHandler

class CsvDataHandler(DataSourceHandler):
    """Handler for uncompressed file datasets."""

    def download_and_extract(self):
        """
        Downloads an uncompressed file directly into the data directory.
        Since CSV is an uncompressed format, no download is necessary.
        """
        pass
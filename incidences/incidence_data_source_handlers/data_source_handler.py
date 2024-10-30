# V3/incidences/incidence_data_source_handlers/data_source_handler.py
import os
import logging
from datetime import datetime
import requests
from abc import ABC, abstractmethod

class DataSourceHandler(ABC):
    """Abstract base class for data download, verification, and management."""

    def __init__(self, source_config, base_data_dir=None, force_download=False):
        self.base_data_dir = base_data_dir or os.path.join(os.path.dirname(__file__), "../../data_sources/incidences")
        self.source_config = source_config
        self.data_dir = os.path.join(self.base_data_dir, source_config["data_dir"])
        self.force_download = force_download
        self.history_file = os.path.join(self.data_dir, "download_history.log")
        self.url = source_config["url"]

    def check_data_exists(self):
        """Check if the data directory already exists."""
        return os.path.exists(self.data_dir)

    def log_download_timestamp(self):
        """Logs a new timestamp in the download history file."""
        timestamp = datetime.now().isoformat()
        with open(self.history_file, "a") as f:
            f.write(f"{timestamp}\nDownloaded data from {self.url}\n")
        logging.info(f"Download timestamp logged: {timestamp}")

    def download_file(self):
        """Downloads a file and returns its path."""
        os.makedirs(self.data_dir, exist_ok=True)
        response = requests.get(self.url, stream=True)
        
        # Attempt to get the file name from the response headers
        content_disposition = response.headers.get('content-disposition')
        if content_disposition:
            # Extract the filename from the content-disposition header if available
            file_name = content_disposition.split("filename=")[-1].strip('"')
        else:
            # Fallback to a default name if content-disposition is not available
            file_name = "downloaded_file"
        
        file_path = os.path.join(self.data_dir, file_name)
        logging.info(f"Downloading data from {self.url}...")
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        logging.info(f"Download completed: {file_path}")
        return file_path

    @abstractmethod
    def download_and_extract(self):
        """To be implemented by subclasses for specific data types."""
        pass
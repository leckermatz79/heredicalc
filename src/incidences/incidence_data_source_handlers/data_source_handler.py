# V3/incidences/incidence_data_source_handlers/data_source_handler.py
import os
import logging
from datetime import datetime
import requests
from abc import ABC, abstractmethod
from src.core.config import PROJECT_ROOT

class DataSourceHandler(ABC):
    """Abstract base class for data download, verification, and management."""

    def __init__(self, source_config, base_data_dir=None, force_download=False):
        self.base_data_dir = base_data_dir or os.path.join(PROJECT_ROOT,"data_sources","incidences")
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
            f.write(f"Downloaded data from {self.url} : {timestamp}\n")
        logging.info(f"Download timestamp logged: {timestamp}")

    def prompt_for_redownload(self):
        """Prompt the user if they want to redownload existing data."""
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                last_download = f.readlines()[-1].strip()
            print(f"Data already exists. \nLast download: {last_download}")
        else:
            print("Data directory exists but no history found.")

        user_input = input("\nDo you want to redownload the data? (y/n): ").strip().lower()
        return user_input == "y"

    def handle_data(self):
        """Main method to handle data download based on conditions."""
        if self.check_data_exists():
            if self.force_download:
                self.clear_data_dir()
                self.download_and_extract()
            elif self.prompt_for_redownload():
                self.clear_data_dir()
                self.download_and_extract()
            else:
                logging.info("Data download skipped.")
        else:
            self.download_and_extract()

    def clear_data_dir(self):
        """Clears all files from the data directory except for the history file."""
        logging.info(f"Clearing data directory: {self.data_dir}")
        for file in os.listdir(self.data_dir):
            file_path = os.path.join(self.data_dir, file)
            if file_path != self.history_file:
                os.remove(file_path)
        logging.info("Data directory cleared except for download history.")

    def download_file(self):
        """Downloads a file and returns its path."""
        os.makedirs(self.data_dir, exist_ok=True)
        response = requests.get(self.url, stream=True)
        
        content_disposition = response.headers.get('content-disposition')
        if content_disposition:
            file_name = content_disposition.split("filename=")[-1].strip('"')
        else:
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
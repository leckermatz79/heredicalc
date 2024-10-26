# V3/incidences/data_handler.py
import os
import requests
import zipfile
import yaml
import logging
from datetime import datetime
import argparse
from V3.setup_logging import setup_logging

class DataHandler:
    """Handles data download, verification, and management for datasets."""
    
    def __init__(self, source_config, base_data_dir=os.path.join(os.path.dirname(__file__), "data"), force_download=False):
        self.source_config = source_config
        self.base_data_dir = base_data_dir
        self.data_dir = os.path.join(base_data_dir, source_config["data_dir"])
        self.force_download = force_download
        self.history_file = os.path.join(self.data_dir, "download_history.log")
        self.zip_url = source_config["url"]
    
    def check_data_exists(self):
        """Check if the data directory already exists."""
        return os.path.exists(self.data_dir)
    
    def log_download_timestamp(self):
        """Logs a new timestamp in the download history file."""
        timestamp = datetime.now().isoformat()
        with open(self.history_file, "a") as f:
            f.write(f"{timestamp} - Downloaded data from {self.zip_url}\n")
        logging.info(f"Download timestamp logged: {timestamp}")
    
    def prompt_for_redownload(self):
        """Prompt the user if they want to redownload existing data."""
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                last_download = f.readlines()[-1].strip()
            print(f"Data already exists. Last download: {last_download}")
        else:
            print("Data directory exists but no history found.")

        user_input = input("Do you want to redownload the data? (y/n): ").strip().lower()
        return user_input == "y"
    
    def download_and_extract(self):
        """Downloads and extracts the data ZIP file."""
        os.makedirs(self.data_dir, exist_ok=True)
        zip_path = os.path.join(self.data_dir, "data.zip")
        
        logging.info(f"Downloading data from {self.zip_url}...")
        response = requests.get(self.zip_url)
        with open(zip_path, "wb") as file:
            file.write(response.content)
        logging.info(f"Download completed: {zip_path}")
        
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(self.data_dir)
        os.remove(zip_path)
        logging.info(f"Data extracted to {self.data_dir}")
        
        self.log_download_timestamp()
    
    def clear_data_dir(self):
        """Clears all files from the data directory except for the history file."""
        logging.info(f"Clearing data directory: {self.data_dir}")
        for file in os.listdir(self.data_dir):
            file_path = os.path.join(self.data_dir, file)
            if file_path != self.history_file:
                os.remove(file_path)
        logging.info("Data directory cleared except for download history.")
    
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

def load_sources():
    """Loads the sources.yaml file and returns the contents."""
    sources_file_name = os.path.join(os.path.dirname(__file__), "sources.yaml")
    with open(sources_file_name, "r") as f:
        return yaml.safe_load(f)

def main():
    # Configure argument parser for CLI options
    parser = argparse.ArgumentParser(description="Data handler for various datasets.")
    parser.add_argument("--dataset", required=True, help="Specify the dataset to download (e.g., ci5_ix)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "SILENT"],
                        help="Set the logging level")
    parser.add_argument("--force-download", action="store_true", help="Force data re-download")
    args = parser.parse_args()

    # Set up logging
    log_level = "CRITICAL" if args.log_level == "SILENT" else args.log_level
    setup_logging(log_level)

    # Load source configuration for the specified dataset
    sources = load_sources()
    if args.dataset not in sources["sources"]:
        logging.error(f"Dataset '{args.dataset}' not found in sources.yaml.")
        return

    source_config = sources["sources"][args.dataset]
    data_handler = DataHandler(source_config, force_download=args.force_download)
    data_handler.handle_data()

if __name__ == "__main__":
    main()
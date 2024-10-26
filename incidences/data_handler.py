# V3/incidences/data_handler.py
import os
import requests
import zipfile
import yaml
import logging
from datetime import datetime
import argparse
from V3.setup_logging import setup_logging
from V3.incidences.parsers.data_parser_factory import DataParserFactory


class DataHandler:
    """Base handler for data download, verification, and management."""

    def __init__(self, source_config, base_data_dir=os.path.join(os.path.dirname(__file__), "data"), force_download=False):
        self.source_config = source_config
        self.base_data_dir = base_data_dir
        self.data_dir = os.path.join(base_data_dir, source_config["data_dir"])
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
            f.write(f"{timestamp} - Downloaded data from {self.url}\n")
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
        
        # Determine the file name from headers or use default name
        if content_disposition:
            file_name = content_disposition.split("filename=")[-1].strip('"')
        else:
            file_name = "downloaded_file"  # Default name if header is missing
        
        file_path = os.path.join(self.data_dir, file_name)

        logging.info(f"Downloading data from {self.url}...")
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        logging.info(f"Download completed: {file_path}")
        
        return file_path  # Returns the actual file path

    def download_and_extract(self):
        """To be implemented by subclasses for specific data types."""
        raise NotImplementedError("Subclasses should implement this method.")

class ZipDataHandler(DataHandler):
    """Handler for ZIP file datasets."""

    def download_and_extract(self):
        """Downloads and extracts the data ZIP file."""
        zip_path = self.download_file()  # Retrieves the actual file path
        
        # Extract all files from the ZIP archive to the data_dir
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(self.data_dir)
        os.remove(zip_path)
        
        logging.info(f"Data extracted to {self.data_dir}")
        self.log_download_timestamp()

class UncompressedDataHandler(DataHandler):
    """Handler for uncompressed file datasets."""

    def download_and_extract(self):
        """Downloads an uncompressed file (no extraction needed)."""
        file_path = self.download_file()  # Get the actual file path
        self.log_download_timestamp()
        logging.info(f"File saved as {file_path}, no extraction required.")

def get_handler(source_config, force_download=False):
    """Factory function to select the appropriate DataHandler."""
    data_format = source_config.get("format", "uncompressed").lower()
    if data_format == "zip":
        return ZipDataHandler(source_config, force_download=force_download)
    elif data_format == "uncompressed":
        return UncompressedDataHandler(source_config, force_download=force_download)
    else:
        raise ValueError(f"Unsupported data format: {data_format}")

def load_sources():
    """Loads the sources.yaml file and returns the contents."""
    sources_path = os.path.join(os.path.dirname(__file__), "sources.yaml")
    with open(sources_path, "r") as f:
        return yaml.safe_load(f)

def load_valid_phenotypes(dataset_name):
    """Load the list of valid phenotype names from the specified dataset in sources.yaml."""
    with open(os.path.join(os.path.dirname(__file__),"sources.yaml"), "r") as file:
        sources_config = yaml.safe_load(file)["sources"]
    
    # Check if the dataset exists in sources.yaml
    if dataset_name not in sources_config:
        raise ValueError(f"Dataset '{dataset_name}' not found in sources.yaml.")
    
    # Extract the phenotype mappings for the specified dataset
    valid_phenotypes = set(sources_config[dataset_name].get("phenotype_mappings", {}).keys())
    return valid_phenotypes

def validate_phenotypes(selected_phenotypes, valid_phenotypes):
    """Check if all selected phenotypes are valid."""
    invalid_phenotypes = [p for p in selected_phenotypes if p not in valid_phenotypes]
    if invalid_phenotypes:
        raise ValueError(f"Invalid phenotypes detected: {', '.join(invalid_phenotypes)}. Please check sources.yaml.")
    print("All selected phenotypes are valid.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Data handler for various datasets.")
    parser.add_argument("--dataset", required=True, help="Specify the dataset to download (e.g., ci5_ix)")
    parser.add_argument("--population", help="Specify the population by key number (e.g., 38402499)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "SILENT"],
                        help="Set the logging level")
    parser.add_argument("--force-download", action="store_true", help="Force data re-download")
    parser.add_argument("--phenotypes",  nargs='+', required=True, help="Specify phenotypes to be included in incidence file (eg, BreastCancer OvarianCancer).")
    args = parser.parse_args()

    # Load and validate phenotypes for the specified dataset
    valid_phenotypes = load_valid_phenotypes(args.dataset)
    validate_phenotypes(args.phenotypes, valid_phenotypes)
    return args

def main():
    args = parse_arguments()
    log_level = "CRITICAL" if args.log_level == "SILENT" else args.log_level
    setup_logging(log_level)

    sources = load_sources()["sources"]
    if args.dataset not in sources:
        logging.error(f"Dataset '{args.dataset}' not found in sources.yaml.")
        return

    source_config = sources[args.dataset]
    data_handler = get_handler(source_config, force_download=args.force_download)
    data_handler.handle_data()
    data_parser = DataParserFactory.create_parser(source_config, population=args.population)
    df = data_parser.parse_population_data()
    logging.info(f"Data for {args.dataset} and population {data_parser.population} processed successfully.")

if __name__ == "__main__":
    main()
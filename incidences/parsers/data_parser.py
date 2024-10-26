# V3/incidences/parsers/data_parser.py
import os
import yaml
import logging
import pandas as pd
from abc import ABC, abstractmethod

class DataParser(ABC):
    """Abstract base class for data parsers."""

    def __init__(self, source_config, population=None):
        self.source_config = source_config
        self.population = population or source_config.get("default_population")
        self.data_dir = os.path.join(os.path.dirname(__file__),"..", "data", source_config["data_dir"])

    def get_population_file_path(self):
        """Determine the correct file path for the given population."""
        file_name = f"{self.population}.csv" # caveat: this could lead to problems in other formats, fine for now (CI5 specific parser)
        file_path = os.path.join(self.data_dir, file_name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file for population {self.population} not found: {file_path}")

        logging.info(f"Using data file: {file_path}")
        return file_path

    @abstractmethod
    def parse_population_data(self):
        """Parse the data for the given population."""
        pass
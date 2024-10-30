# V3/incidences/incidence_models/incidence_data_model.py
import os
import yaml
import logging
import pandas as pd
from abc import ABC, abstractmethod

class IncidenceDataModel(ABC):
    """Abstract base class for data parsers."""

    def __init__(self, source_config, population=None):
        self.source_config = source_config
        self.population = population or source_config.get("default_population")
        self.data_dir = os.path.join(os.path.dirname(__file__),"..", "data", source_config["data_dir"])
        self.phenotype_mappings = source_config.get("phenotype_mappings", {})
        self.column_mappings = self.source_config.get("column_mappings", {})
        self.gender_mapping = self.source_config.get("gender_mapping", {})

    def get_column(self, column_name, df):
        """
        Retrieve the column from the DataFrame based on the specified column mappings.
        
        Parameters:
            column_name (str): The column name in column_mappings (e.g., "gender_col").
            df (pd.DataFrame): The DataFrame containing the data.
        
        Returns:
            The column (Series) from the DataFrame.
        """
        col_spec = self.column_mappings.get(column_name)
        if isinstance(col_spec, int) and col_spec >= 0:
            # Treat as column index if it is a positive integer
            return df.iloc[:, col_spec]
        elif isinstance(col_spec, str):
            # Check if the DataFrame has headers
            if not isinstance(df.columns, pd.Index) or not df.columns.is_object():
                raise ValueError(f"The dataset for '{column_name}' requires a header row, which is missing.")
            return df[col_spec]  # Column as name
        else:
            raise ValueError(f"Invalid column specification for '{column_name}' in sources.yaml.")
        
    def filter_by_phenotypes(self, df, phenotypes):
        """
        Filter data by phenotypes based on the mappings in sources.yaml.
        
        Parameters:
            df (pd.DataFrame): Data to be filtered.
            phenotypes (list): List of canonical phenotype names from CLI.
        
        Returns:
            pd.DataFrame: Filtered data.
        """
        # Collect all mapped IDs for the selected phenotypes
        phenotype_ids = []
        for phenotype in phenotypes:
            mapped_ids = self.phenotype_mappings.get(phenotype, [])
            if not mapped_ids:
                print(f"Warning: Phenotype '{phenotype}' not found in mappings.")
            phenotype_ids.extend(mapped_ids)
        
        # Filter data by phenotype IDs in the 'phenotype' column
        filtered_df = df[df["phenotype"].isin(phenotype_ids)]
        logging.info(f"Data filtered to include phenotypes: {phenotypes} (IDs: {phenotype_ids})")
        
        return filtered_df
    
    def get_population_file_path(self):
        """Determine the correct file path for the given population."""
        file_name = f"{self.population}.csv" # caveat: this could lead to problems in other formats, fine for now (CI5 specific parser)
        file_path = os.path.join(self.data_dir, file_name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file for population {self.population} not found: {file_path}")

        logging.info(f"Using data file: {file_path}")
        return file_path

    @abstractmethod
    def parse_data(self, df):
        """Abstract method to be implemented in subclasses."""
        raise NotImplementedError("Subclasses should implement this method (parse_data).")
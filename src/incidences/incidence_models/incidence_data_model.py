incidences/incidence_models/incidence_data_model.py
import os
import logging
import pandas as pd
from abc import ABC, abstractmethod
from src.core.config import PROJECT_ROOT


class IncidenceDataModel(ABC):
    """Abstract base class for data parsers."""

    def __init__(self, source_config, population=None):
        self.source_config = source_config
        self.population = population or source_config.get("default_population")
        self.base_data_dir = os.path.join(PROJECT_ROOT,"data_sources","incidences")
        self.data_dir = os.path.join(self.base_data_dir, source_config["data_dir"])
        self.phenotype_mappings = source_config.get("phenotype_mappings", {})
        self.column_mappings = self.source_config.get("column_mappings", {})
        self.gender_mapping = self.source_config.get("gender_mapping", {})

    def calculate_incidence_rate(self, cases, person_years):
        """
        Calculate the incidence rate for given cases and person-years.

        Parameters:
            cases (int): Number of cases observed.
            person_years (int): Observed person-years.

        Returns:
            float: Calculated incidence rate (lambda).
        """
        try:
            if person_years > 0:
                incidence_rate = cases / person_years
                logging.debug(f"Calculated incidence rate: {incidence_rate} for cases: {cases}, person-years: {person_years}")
                return incidence_rate
            else:
                logging.warning("Person-years must be greater than zero for incidence rate calculation.")
                return 0.0
        except Exception as e:
            logging.error(f"Error calculating incidence rate: {e}")
            return None
        
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

    def  add_age_span_column(self, data_frame):
        """
        Default implementation to add an 'age_span' column to the DataFrame.
        
        Parameters:
            data_frame (pd.DataFrame): The incidence data DataFrame.
        
        Returns:
            pd.DataFrame: Updated DataFrame with an 'age_span' column.
        """
        if 'age_class_lower' in data_frame.columns and 'age_class_upper' in data_frame.columns:
            data_frame['age_span'] = data_frame.apply(
                lambda row: (row['age_class_upper'] - row['age_class_lower'])+1 if pd.notnull(row['age_class_upper']) else "open-ended",
                axis=1
            )
            logging.info("Default age span column added.")
        else:
            logging.warning("Age group columns not found; skipping age span calculation.")
        return data_frame

    @abstractmethod
    def parse_data(self, df):
        """Abstract method to be implemented in subclasses."""
        raise NotImplementedError("Subclasses should implement this method (parse_data).")
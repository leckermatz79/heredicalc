# penetrances/crhf_models/constant_crhf_model.py

import os
import pandas as pd
import logging
from .crhf_model import CRHFModel

class ConstantCRHFModel(CRHFModel):
    """
    Constant CRHF model where the CRHF value is independent of age, gender, and phenotype.
    
    This model loads a constant CRHF value from a CSV file and provides it for the specified gene.
    """

    def __init__(self, gene, data_frame, crhf_file_path=None):
        """
        Initialize the ConstantCRHFModel with a specific gene and data frame.

        Parameters:
            gene (str): The gene for which to calculate CRHF.
            data_frame (pd.DataFrame): DataFrame with phenotype, gender, age class, etc.
            crhf_file_path (str): Path to the CSV file with constant CRHF values.
        """
        super().__init__(gene, data_frame)
        self.crhf_file_path = crhf_file_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "data_sources", "penetrances", "crhf", "constant_crhf_model.csv"
        )
        self.crhf_value = self._load_crhf_value()

    def _load_crhf_value(self):
        """
        Load the CRHF value for the specified gene from the CSV file.
        
        Returns:
            float: The CRHF value for the gene.
        """
        try:
            crhf_df = pd.read_csv(self.crhf_file_path)
            if 'gene' not in crhf_df.columns:
                raise ValueError(f"'gene' column not found in CRHF file {self.crhf_file_path}")
 
            crhf_row = crhf_df[crhf_df['gene'] == self.gene]
            if crhf_row.empty:
                logging.warning(f"CRHF value for gene '{self.gene}' not found. Using default of 0.0.")
                return 0.0

            crhf_value = crhf_row.iloc[0]['crhf_value']
            logging.info(f"Loaded CRHF value {crhf_value} for gene {self.gene}.")
            return crhf_value
        except FileNotFoundError:
            logging.error(f"CRHF file not found at {self.crhf_file_path}. Using default value of 0.0.")
            return 0.0
        except Exception as e:
            logging.error(f"Error loading CRHF value for gene {self.gene}: {e}")
            return 0.0

    def calculate_crhf(self, gender, ager):
        """
        Return the constant CRHF value for the given gender and age class.

        Parameters:
            gender (str): Gender of the individual ("M" or "F").
            age (float): Age for which CRHF is to be calculated.
        
        Returns:
            float: The constant CRHF value.
        """
        # Simply return the preloaded constant CRHF value, as it does not depend on gender or age.
        return self.crhf_value
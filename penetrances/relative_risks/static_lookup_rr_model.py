# V3/penetrances/relative_risks/static_lookup_rr_model.py
import pandas as pd
import os
import logging
from V3.penetrances.relative_risks.relative_risk_model import RelativeRiskModel

class StaticLookupRRModel(RelativeRiskModel):
    """
    Model for calculating relative risks using a static lookup table.
    
    This model loads relative risk data from gene-specific CSV files and provides
    relative risk values based on age, phenotype, and gender.
    """

    def __init__(self, gene, data_dir=None):
        """
        Initialize the StaticLookupRRModel with a specific gene and data directory.
        
        Parameters:
            gene (str): The gene symbol to load relative risk data for (e.g., "BRCA1").
            data_dir (str): Path to the directory containing relative risk CSV files.
        """
        # Define the default path based on the file location
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data_sources", "relative_risks", "static_lookup_tables")

        self.gene = gene
        self.data_dir = data_dir
        self.lookup_table = self._load_lookup_table()

    def _load_lookup_table(self):
        """
        Load the relative risk lookup table for the specified gene from a CSV file.
        
        Returns:
            pd.DataFrame: DataFrame containing relative risks for the gene.
        
        Raises:
            FileNotFoundError: If the file for the gene does not exist.
        """
        file_path = os.path.join(self.data_dir, f"{self.gene}.csv")
        if not os.path.isfile(file_path):
            logging.error(f"Relative risk file for gene '{self.gene}' not found at {file_path}")
            raise FileNotFoundError(f"Relative risk file for gene '{self.gene}' not found.")
        
        # Load the CSV file into a DataFrame
        logging.info(f"Loading relative risk data from {file_path}")
        df = pd.read_csv(file_path)
        
        # Validate columns are as expected
        required_columns = {"gender", "age_from", "age_to", "phenotype", "heterozygous_rr", "homozygous_rr"}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"CSV file for {self.gene} is missing required columns: {required_columns - set(df.columns)}")
        return df

    def get_relative_risk(self, age, phenotype, gender):
        """
        Get the relative risk for a given age, phenotype, and gender.
        
        Parameters:
            age (int): Age of the individual.
            phenotype (str): The phenotype of interest (e.g., "BreastCancer").
            gender (str): Gender of the individual ("M" or "F").
        
        Returns:
            tuple: (heterozygous_risk, homozygous_risk) for the given parameters.
        """
        # Filter the lookup table by phenotype and gender
        filtered_df = self.lookup_table[
            (self.lookup_table["phenotype"] == phenotype) &
            (self.lookup_table["gender"] == gender) &
            (self.lookup_table["age_from"] <= age) &
            ((self.lookup_table["age_to"] >= age) | (self.lookup_table["age_to"].isna()))
        ]

        if filtered_df.empty:
            logging.warning(f"No relative risk data found for {self.gene} with age={age}, phenotype={phenotype}, gender={gender}")
            return None, None
        
        # Retrieve the risks for the first matched row (assuming non-overlapping ranges)
        heterozygous_risk = filtered_df.iloc[0]["heterozygous_rr"]
        homozygous_risk = filtered_df.iloc[0]["homozygous_rr"]

        logging.info(f"Retrieved RR for {self.gene}, age={age}, phenotype={phenotype}, gender={gender}: "
                     f"Heterozygous={heterozygous_risk}, Homozygous={homozygous_risk}")
        
        return heterozygous_risk, homozygous_risk
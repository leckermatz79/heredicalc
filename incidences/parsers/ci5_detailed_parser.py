# V3/incidences/parsers/ci5_detailed_parser.py
from V3.incidences.parsers.data_parser import DataParser
import pandas as pd
import logging

class CI5DetailedParser(DataParser):
    """Parser for CI5 detailed data format."""

    def parse_population_data(self):
        """Parse the CSV data file for the selected population in CI5 detailed format."""
        file_path = self.get_population_file_path()
        df = pd.read_csv(file_path)
        # Example data processing specific to CI5 detailed
        logging.info(f"Parsed CI5 detailed data for population {self.population}")
        return df
    
    def parse_data(self, df):
        """Parse CI5_detailed-formatted data with specific columns for gender, phenotype, age, cases, and person-years."""
        gender = self.get_column("gender_col", df)
        phenotype = self.get_column("phenotype_col", df)
        age = self.get_column("age_col", df)
        cases = self.get_column("cases_col", df)
        person_years = self.get_column("person_years_col", df)

        # Combine parsed data into a standardized DataFrame for further processing
        parsed_df = pd.DataFrame({
            "gender": gender,
            "phenotype": phenotype,
            "age": age,
            "cases": cases,
            "person_years": person_years
        })
        
        return parsed_df
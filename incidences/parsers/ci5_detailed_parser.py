# V3/incidences/parsers/ci5_detailed_parser.py
from V3.incidences.parsers.data_parser import DataParser
import pandas as pd
import logging

class CI5DetailedParser(DataParser):
    """Parser for CI5 detailed data format."""
    def parse_data(self, df=None):
        """Parse the CSV data file for the selected population in CI5 detailed format."""
        if df is None:
            file_path = self.get_population_file_path()
            has_header = self.source_config.get("has_header", False)
            df = pd.read_csv(file_path, header=0 if has_header else None)
        
        # get_column retrieves column name or numbers and respects a present header line. 
        gender = self.get_column("gender_col", df)
        phenotype = self.get_column("phenotype_col", df)
        age = self.get_column("age_col", df)
        cases = self.get_column("cases_col", df)
        person_years = self.get_column("person_years_col", df)

        # Combine parsed data into a consistent DataFrame for further processing
        parsed_df = pd.DataFrame({
            "gender": gender,
            "phenotype": phenotype,
            "age": age,
            "cases": cases,
            "person_years": person_years
        })
        
        return parsed_df
    
    def build_incidence_table(self, df):
        """
        Build the incidence table by transforming gender, splitting age into bounds,
        and resetting the index with the name 'incidence_class'.
        
        Parameters:
            df (pd.DataFrame): The filtered DataFrame with raw gender and age columns.
        
        Returns:
            pd.DataFrame: The incidence table with readable gender, split age bounds, and reset index.
        """
        # Transform gender to readable format
        gender_col = "gender"
        df[gender_col] = df[gender_col].map(
            {self.gender_mapping.get("male", 1): "M",
             self.gender_mapping.get("female", 2): "F"}
        ).fillna("U")  # Default to 'U' if gender is unrecognized

        # Split age into lower and upper bounds using the index as age class ID
        age_class_ranges = [self.get_age_range(age_class_id) for age_class_id in df["age"]]
        df[["age_class_lower", "age_class_upper"]] = pd.DataFrame(age_class_ranges, index=df.index)

        # Reset index and rename it to 'incidence_class'
        df.reset_index(drop=True, inplace=True)
        df.index.name = "incidence_class"
        
        # Select relevant columns
        incidence_table = df[["gender", "phenotype", "age_class_lower", "age_class_upper", "cases", "person_years"]]
        return incidence_table
    
    def get_age_range(self, age_class_id):
        """Return the age range (lower, upper) for a given age class ID based on sources.yaml."""
        age_structure = self.source_config.get("age_structure", {})
        age_groups = age_structure.get("age_groups", [])

        # Adjust for 1-based indexing in age_class_id by subtracting 1
        adjusted_index = age_class_id - 1

        # Verify age_class_id is a valid index
        try:
            age_range = age_groups[adjusted_index]
        except IndexError:
            logging.warning(f"Age class ID '{age_class_id}' (adjusted to index '{adjusted_index}') is out of range.")
            return None, None

        return age_range.get("min", None), age_range.get("max", None)
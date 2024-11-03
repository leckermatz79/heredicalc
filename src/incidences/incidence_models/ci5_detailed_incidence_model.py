# incidences/incidence_models/ci5_detailed_incidence_model.py
from .incidence_data_model import IncidenceDataModel
import pandas as pd
import logging

class CI5DetailedIncidenceModel(IncidenceDataModel):
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
        replacing phenotype IDs with canonical names, and aggregating cases for multi-ID phenotypes.
        
        Parameters:
            df (pd.DataFrame): The filtered DataFrame with raw gender, age, and phenotype columns.
        
        Returns:
            pd.DataFrame: The final incidence table with readable gender, aggregated cases,
                          and single rows for each age, gender, and phenotype combination.
        """
        # Transform gender to readable format
        gender_col = "gender" # "gender" is name of the gender column in our interim incidence data frame.
        df[gender_col] = df[gender_col].map(
            {self.gender_mapping.get("male", 1): "M",
             self.gender_mapping.get("female", 2): "F"}
        ).fillna("U")  # Default to 'U' if gender is unrecognized

        # Apply age range transformation with the correct index offset for age_class_id
        df[["age_class_lower", "age_class_upper"]] = df["age"].apply(lambda x: self.get_age_range(x - 1)).apply(pd.Series)

        # Replace phenotype IDs with canonical phenotype names
        phenotype_map = {id_: phenotype for phenotype, ids in self.phenotype_mappings.items() for id_ in ids}
        df["phenotype"] = df["phenotype"].map(phenotype_map)

        # Create a new DataFrame to aggregate cases and person years for each unique combination
        incidence_table = (
            df.groupby(["age_class_lower", "age_class_upper", "phenotype", "gender"], dropna=False, as_index=False)
            .agg({"cases": "sum", "person_years": "first"})  # Sum cases and keep person_years
        )

        # Sort the incidence_table by phenotype, gender, and age_class_lower
        incidence_table.sort_values(by=["phenotype", "gender", "age_class_lower"], inplace=True)

        # Reset index and rename it to 'incidence_class'
        incidence_table.reset_index(drop=True, inplace=True)
        incidence_table.index.name = "incidence_class"

        # Reorder columns as specified
        incidence_table = incidence_table[["gender", "phenotype", "age_class_lower", "age_class_upper", "cases", "person_years"]]
        self.data_frame = incidence_table
        
        return incidence_table
    
    def add_incidence_rate_column(self):
        """
        Add an incidence rate column to the incidence DataFrame.
        
        Returns:
            pd.DataFrame: Updated DataFrame with an 'incidence_rate' column.
        """
        self.data_frame['incidence_rate'] = self.data_frame.apply(
            lambda row: self.calculate_incidence_rate(row['cases'], row['person_years']),
            axis=1
        )
        logging.info("Incidence rate column added to the DataFrame.")
        return self.data_frame

    def get_age_range(self, age_class_id):
        """Return the age range (lower, upper) for a given age class ID based on sources.yaml."""
        age_structure = self.source_config.get("age_structure", {})
        age_groups = age_structure.get("age_groups", [])
        unknown_age_class = age_structure.get("unknown_age_class", None)
        open_ended_age_class = age_structure.get("open_ended_age_class", None)

        # Check for 'Unknown' age class
        if age_class_id == unknown_age_class:
            return None, None

        # Check for open-ended age class
        if age_class_id == open_ended_age_class:
            age_range = age_groups[age_class_id]
            return age_range.get("min", None), None  # No upper bound for open-ended age group

        # Standard age range
        try:
            age_range = age_groups[age_class_id]
        except IndexError:
            logging.warning(f"Age class ID '{age_class_id}' is out of range.")
            return None, None

        return age_range.get("min", None), age_range.get("max", None)
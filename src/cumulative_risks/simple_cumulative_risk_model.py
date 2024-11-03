# cumulative_risks/simple_cumulative_risk_model.py

import logging
import numpy as np
import pandas as pd
from .cumulative_risk_model import CumulativeRiskModel

class SimpleCumulativeRiskModel(CumulativeRiskModel):
    """
    A simple cumulative risk model under the assumption of independent phenotypes.
    """

    def __init(self, data_frame):
        """
        Initializes the SimpleCumulativeRiskModel with the incidence data.
        """
        super().__init__(data_frame)
    
    def calculate_cumulative_risk(self, gender, age_class_upper, phenotypes):
        """
        Calculate cumulative risk for a given gender, age upper limit, and selected phenotypes.
        
        Parameters:
            gender (str): The gender to filter data ('M' or 'F').
            age_class_upper (float): The upper age limit up to which cumulative risk is calculated.
            phenotypes (list): List of phenotypes to include in risk calculation.
        
        Returns:
            float: The cumulative risk for the specified parameters.
        """
        # Filter the DataFrame for specified gender, age limit, and phenotypes
        relevant_data = self.data_frame[
            (self.data_frame['gender'] == gender) &
            (self.data_frame['phenotype'].isin(phenotypes)) &
            (self.data_frame['age_class_upper'] <= age_class_upper)
        ].copy()

        # Calculate cumulative risk for the filtered subset
        return self._calculate_risk_for_subset(relevant_data)

    def _calculate_risk_for_subset(self, subset_df):
        """
        Helper function to calculate cumulative risk from a subset of the data.
        
        Parameters:
            subset_df (pd.DataFrame): Filtered DataFrame containing relevant incidence data.
        
        Returns:
            float: Cumulative risk calculated for the subset.
        """
        # Ensure subset_df has required columns
        if not {'incidence_rate', 'age_span'}.issubset(subset_df.columns):
            raise ValueError("Data frame must contain 'incidence_rate' and 'age_span' columns.")

        # Sum the contributions of each age-phenotype combination
        subset_df.loc[:, 'risk_contribution'] = subset_df['incidence_rate'] * subset_df['age_span']
        total_risk_contribution = subset_df['risk_contribution'].sum()

        # Calculate cumulative risk
        cumulative_risk = 1 - np.exp(-total_risk_contribution)
        logging.info(f"Cumulative risk calculated: {cumulative_risk}")
        
        return cumulative_risk
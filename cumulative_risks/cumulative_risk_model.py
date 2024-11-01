# V3/cumulative_risks/cumulative_risk_model.py

from abc import ABC, abstractmethod
import pandas as pd
import logging

class CumulativeRiskModel(ABC):
    """
    Abstract base class for calculating cumulative risks.
    
    This class provides a structure for implementing different models of cumulative risk
    based on incidence data.
    
    Parameters:
        incidence_data (pd.DataFrame): DataFrame with incidence rates, age spans, and other relevant columns.
    """
    
    def __init__(self, incidence_data):
        if not isinstance(incidence_data, pd.DataFrame):
            raise TypeError("Incidence data must be a pandas DataFrame.")
        
        self.incidence_data = incidence_data

    @abstractmethod
    def calculate_cumulative_risk(self):
        """
        Abstract method to calculate cumulative risk based on the model's specific algorithm.
        
        Returns:
            float: Cumulative risk value or a DataFrame with cumulative risk per age group.
        
        Raises:
            NotImplementedError: This method should be overridden in a subclass.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate_incidence_data(self):
        """
        Validates the incidence data for required columns.
        
        Required columns: 'age_span', 'incidence_rate', 'phenotype', 'gender'
        
        Raises:
            ValueError: If required columns are missing in the incidence data.
        """
        required_columns = {'age_span', 'incidence_rate', 'phenotype', 'gender'}
        missing_columns = required_columns - set(self.incidence_data.columns)
        if missing_columns:
            raise ValueError(f"Missing columns in incidence data: {', '.join(missing_columns)}")
        
        logging.debug("Incidence data validation successful.")
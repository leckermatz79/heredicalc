# cumulative_risks/cumulative_risk_model_factory.py

import logging
from .cumulative_risk_model import CumulativeRiskModel
from .simple_cumulative_risk_model import SimpleCumulativeRiskModel
from ..incidences.incidence_models import incidence_data_model
# Import other specific models here as they are implemented

class CumulativeRiskModelFactory:
    """
    Factory class to create instances of CumulativeRiskModel subclasses.
    
    Provides an interface to create various cumulative risk models based on a specified model type.
    """
    def __init__(self, data_frame):
        """
        Initializes the cumulative risk model with incidence data.

        Parameters:
            data_frame (pd.DataFrame): DataFrame containing incidence data (e.g., rates, age spans, etc.)
        """
        self.data_frame = data_frame

    @staticmethod
    def create_model(model_type, incidence_data):
        """
        Creates an instance of a specific cumulative risk model.
        
        Parameters:
            model_type (str): Type of the cumulative risk model (e.g., 'simple').
            incidence_data (pd.DataFrame): DataFrame with incidence data.
        
        Returns:
            CumulativeRiskModel: An instance of a cumulative risk model subclass.
        
        Raises:
            ValueError: If the specified model type is unsupported.
        """
        
        if model_type == 'simple':
            logging.debug("Creating SimpleCumulativeRiskModel instance.")
            return SimpleCumulativeRiskModel(incidence_data)
        # Add more model types here as needed
        else:
            raise ValueError(f"Unsupported cumulative risk model type: {model_type}")
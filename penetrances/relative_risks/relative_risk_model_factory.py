# V3/penetrances/relative_risks/relative_risk_model_factory.py

import logging
from V3.penetrances.relative_risks.static_lookup_rr_model import StaticLookupRRModel

class RelativeRiskModelFactory:
    """
    Factory class to create relative risk model instances based on specified model type.
    This allows flexible creation of different relative risk models as needed.
    """
    
    @staticmethod
    def create_model(model_type, gene=None, data_frame=None, rr_file_path=None):
        """
        Create a relative risk model based on the specified model type.
        
        Parameters:
            model_type (str): The type of relative risk model (e.g., "static_lookup").
            gene (str): The gene symbol for which the relative risk model should be created.

        Returns:
            RelativeRiskModel: An instance of a specific relative risk model.
        
        Raises:
            ValueError: If the specified model type is not supported.
        """
        if model_type == "static_lookup":
            logging.debug(f"Creating StaticLookupRRModel instance for gene '{gene}'.")
            return StaticLookupRRModel(gene, data_frame, rr_file_path)
        else:
            raise ValueError(f"Unknown relative risk model type: {model_type}")
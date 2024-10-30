# V3/penetrances/crhf_models/constant_crhf_model.py
import yaml
import os
import logging
from .crhf_model import CRHFModel

class ConstantCRHFModel(CRHFModel):
    """
    Constant CRHF model that provides a fixed CRHF for a specified gene.
    
    This model assumes a single constant CRHF per gene across all age group, genders and populations.
    """
    
    def __init__(self):
        # Load CRHF values from YAML file
        crhf_path = os.path.join(os.path.dirname(__file__), "crhf.yaml")
        try:
            with open(crhf_path, "r") as file:
                self.crhf_values = yaml.safe_load(file).get("constant", {})
            logging.info("Loaded CRHF values successfully.")
        except FileNotFoundError:
            logging.error(f"CRHF YAML file not found at {crhf_path}.")
            self.crhf_values = {}

    def get_crhf(self, gene):
        """Retrieve the constant CRHF value for a specific gene."""
        crhf_value = self.crhf_values.get(gene)
        if crhf_value is None:
            logging.warning(f"CRHF value for gene '{gene}' not found.")
            return None
        logging.info(f"CRHF for {gene}: {crhf_value}")
        return crhf_value

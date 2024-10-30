# V3/penetrances/relative_risk_models.py
from abc import ABC, abstractmethod
import logging
import pandas as pd
import os

class RelativeRiskModel(ABC):
    """
    Abstract base class for calculating relative risks based on age, phenotype, and gender.
    """

    @abstractmethod
    def get_relative_risk(self, age, phenotype, gender):
        """
        Abstract method to get relative risk based on age, phenotype, and gender.
        
        Parameters:
            age (int): The specific age.
            phenotype (str): Phenotype (e.g., "BreastCancer", "LungCancer").
            gender (str): Gender (e.g., "M" or "F").
        
        Returns:
            tuple: (heterozygous_risk, homozygous_risk) relative risk values.
        """
        pass
    
class RelativeRiskModelFactory:
    """
    Factory class to create a RelativeRiskModel instance based on the model type.
    """

    @staticmethod
    def create_relative_risk_model(model_type, **kwargs):
        if model_type == "static":
            return StaticLookupRRModel()
        # elif model_type == "normal_distribution":
        #     return NormalDistributionRiskModel(**kwargs)
        else:
            raise ValueError(f"Unsupported relative risk model type: {model_type}")
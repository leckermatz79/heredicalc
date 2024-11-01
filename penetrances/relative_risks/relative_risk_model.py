# V3/penetrances/relative_risks/relative_risk_model.py
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
    

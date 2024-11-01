# V3/penetrances/relative_risks/relative_risk_model.py
from abc import ABC, abstractmethod
from typing import Tuple

class RelativeRiskModel(ABC):
    """
    Abstract base class for relative risk models.
    
    This class defines the interface for calculating relative risks based on age,
    phenotype, and gender for specific genes.
    """

    @abstractmethod
    def calculate_relative_risk(self, age: int, phenotype: str, gender: str) -> Tuple[float, float]:
        """
        Calculate the relative risk for a given age, phenotype, and gender.
        
        Parameters:
            age (int): Age of the individual.
            phenotype (str): The phenotype of interest (e.g., "BreastCancer").
            gender (str): Gender of the individual ("M" or "F").
        
        Returns:
            Tuple[float, float]: A tuple containing the heterozygous and homozygous risk values.
        
        Raises:
            NotImplementedError: If this method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement this method.")
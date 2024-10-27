# V3/penetrances/penetrance_models.py
from abc import ABC, abstractmethod
import logging

class PenetranceModel(ABC):
    """
    Abstract base class for calculating penetrance based on a given incidence table, 
    CRHF values, and relative risks.
    """
    
    def __init__(self, incidence_table, crhf_model, relative_risks):
        self.incidence_table = incidence_table
        self.crhf_model = crhf_model
        self.relative_risks = relative_risks
    
    @abstractmethod
    def calculate_penetrance(self):
        """
        Abstract method for calculating penetrance. To be implemented by subclasses.
        """
        pass

class SimpleDistributionPenetranceModel(PenetranceModel):
    """
    A simple penetrance model that assumes cases are uniformly distributed within each age group.
    """

    def calculate_penetrance(self):
        """
        Calculates penetrance by uniformly distributing cases within each age group.
        
        Returns:
            DataFrame: A modified incidence table with calculated penetrance values.
        """
        logging.info("Calculating penetrance using the simple distribution model.")
        
        # Placeholder logic for simple uniform distribution
        for index, row in self.incidence_table.iterrows():
            crhf = self.crhf_model.get_crhf(row['phenotype'])
            risk_factor = self.relative_risks.get(row['age_class'], 1)  # Default risk factor is 1 if age_class is not in relative risks
            row['penetrance'] = row['cases'] * crhf * risk_factor / row['person_years']
        
        return self.incidence_table

class PenetranceModelFactory:
    """
    Factory class to create a PenetranceModel instance based on the provided model type.
    """

    @staticmethod
    def create_penetrance_model(model_type, incidence_table, crhf_model, relative_risks):
        if model_type == "simple_distribution":
            return SimpleDistributionPenetranceModel(incidence_table, crhf_model, relative_risks)
        else:
            raise ValueError(f"Unsupported penetrance model type: {model_type}")
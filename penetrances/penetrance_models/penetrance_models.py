# V3/penetrances/penetrance_models/penetrance_models.py
import logging
from abc import ABC, abstractmethod
from V3.penetrances.relative_risk.relative_risk_models import RelativeRiskModel
from V3.penetrances.crhf_models import CRHFModel
import pandas as pd


class PenetranceModel(ABC):
    """
    Abstract base class for calculating penetrance.
    """
    def __init__(self, incidence_data, relative_risk_model: RelativeRiskModel, crhf_model: CRHFModel):
        self.incidence_data = incidence_data
        self.relative_risk_model = relative_risk_model
        self.crhf_model = crhf_model
        logging.debug("Initialized PenetranceModel with incidence data and models.")

    @abstractmethod
    def calculate_penetrance(self, gene, phenotype):
        """
        Abstract method to calculate penetrance for a given gene and phenotype.
        
        Raises:
            NotImplementedError: Must be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")
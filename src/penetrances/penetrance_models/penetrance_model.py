# V3/penetrances/penetrance_models/penetrance_model.py
from abc import ABC, abstractmethod

class PenetranceModel(ABC):
    """
    Abstract base class for calculating penetrance.
    """
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def calculate_penetrance(self, *args, **kwargs):
        """
        Abstract method to calculate penetrance for a given gene and phenotype.
        
        Raises:
            NotImplementedError: Must be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")
# V3/penetrances/crhf_models/crhf_model.py
import yaml
import os
import logging
from abc import ABC, abstractmethod

class CRHFModel(ABC):
    """
    Abstract base class for CRHF models.
    
    Subclasses must implement the `get_crhf` method to calculate 
    the CRHF (carrier risk heterozygous frequency) for a specific gene.
    """
    
    @abstractmethod
    def get_crhf(self, gene):
        """
        Retrieve the CRHF for a given gene.
        
        Parameters:
            gene (str): Gene symbol for which to get the CRHF.
        
        Returns:
            float: The CRHF value.
        
        Raises:
            NotImplementedError: If subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses should implement this method.")
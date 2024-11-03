# V3/penetrances/crhf_models/crhf_model.py

from abc import ABC, abstractmethod

class CRHFModel(ABC):
    """
    Abstract base class for CRHF models.
    
    Subclasses must implement the `calculate_crhf` method to retrieve
    the CRHF (carrier risk heterozygous frequency) for a specific gene,
    given certain parameters like gender and age class.
    """
    
    def __init__(self, gene, data_frame):
        """
        Initialize the CRHFModel with gene and data frame.
        
        Parameters:
            gene (str): Gene symbol for which to calculate CRHF.
            data_frame (pd.DataFrame): Data containing information such as phenotype, age, and gender.
        """
        self.gene = gene
        self.data_frame = data_frame

    @abstractmethod
    def calculate_crhf(self, gender, age_class_upper):
        """
        Retrieve the CRHF for a given gene, gender, and age class.
        
        Parameters:
            gender (str): Gender of the individual ("M" or "F").
            age_class_upper (float): Upper age limit for the age class.
        
        Returns:
            float: The calculated CRHF value.
        
        Raises:
            NotImplementedError: If subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses should implement this method.")
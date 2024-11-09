# pedconv/importers/pedigree_importer.py

from abc import ABC, abstractmethod

class PedigreeImporter(ABC):
    """
    Abstract base class for importing pedigree data from different formats.
    
    Subclasses should implement the `import_data` method to load pedigree data
    and return it as a DataFrame in the expected structure.
    """
    
    def __init__(self, file_path):
        """
        Initializes the PedigreeImporter with a file path.

        Parameters:
            file_path (str): Path to the file containing pedigree data.
        """
        self.file_path = file_path

    @abstractmethod
    def import_data(self):
        """
        Abstract method to import pedigree data. Should return a DataFrame
        with the following columns:
        ['id', 'pseudonym', 'father_id', 'mother_id', 'gender', 'phenotypes', 
        'age_last_seen', 'death_age'].

        Returns:
            pd.DataFrame: DataFrame with pedigree information.
        """
        pass
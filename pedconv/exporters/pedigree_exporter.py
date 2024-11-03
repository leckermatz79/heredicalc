# pedconv/exporters/pedigree_exporter.py

from abc import ABC, abstractmethod

class PedigreeExporter(ABC):
    """
    Abstract base class for exporting pedigree data in various formats.
    """

    @abstractmethod
    def export_data(self, pedigree, file_path):
        """
        Exports pedigree data to a specified file path.

        Parameters:
            pedigree (Pedigree): The Pedigree instance to export.
            file_path (str): Path to the file where data should be exported.
        """
        pass
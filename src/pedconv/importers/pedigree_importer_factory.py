# pedconv/importers/pedigree_importer_factory.py

from .cool_pedigree_importer import CoolPedigreeImporter

class PedigreeImporterFactory:
    """
    Factory class to create specific pedigree importer instances based on file type.
    """

    @staticmethod
    def create_importer(importer_type, file_path):
        """
        Create a specific PedigreeImporter instance based on file type.

        Parameters:
            file_type (str): The type of the file format (e.g., "cool").
            file_path (str): The path to the pedigree file.

        Returns:
            PedigreeImporter: An instance of a specific PedigreeImporter.

        Raises:
            ValueError: If the specified file type is not supported.
        """
        if importer_type.lower() == "cool":
            return CoolPedigreeImporter(file_path)
        else:
            raise ValueError(f"Unsupported file type: {importer_type}")
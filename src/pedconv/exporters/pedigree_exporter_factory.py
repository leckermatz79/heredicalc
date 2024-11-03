# pedconv/exporters/pedigree_exporter_factory.py

import logging
#from .pedigree_exporter import PedigreeExporter
#from .csv_pedigree_exporter import CsvPedigreeExporter  
from .cool_pedigree_exporter import CoolPedigreeExporter  
from .segregatr_flb_pedigree_exporter import SegregatrFLBPedigreeExporter


class PedigreeExporterFactory:
    """
    Factory class to create pedigree exporter instances based on specified exporter type.
    """

    @staticmethod
    def create_exporter(exporter_type, file_path):
        """
        Create a pedigree exporter based on the specified type.

        Parameters:
            exporter_type (str): The type of exporter (e.g., "csv").

        Returns:
            PedigreeExporter: An instance of a specific pedigree exporter.

        Raises:
            ValueError: If the specified exporter type is not supported.
        """
        if exporter_type == "cool":
            logging.debug("Creating CoolPedigreeExporter instance.")
            return CoolPedigreeExporter(file_path)
        #elif exporter_type == "csv":
        #    logging.debug("Creating CsvPedigreeExporter instance.")
        #    return CsvPedigreeExporter(file_path)
        elif exporter_type == "segregatr_flb":
            logging.debug("Creating SegregatrFlbPedigreeExporter instance.")
            return SegregatrFLBPedigreeExporter(file_path)
        else:
            raise ValueError(f"Unknown pedigree exporter type: {exporter_type}")
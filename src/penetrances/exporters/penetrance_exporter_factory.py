# src/penetrances/exporters/penetrance_exporter_factory.py

import logging
from .penetrance_exporter import PenetranceExporter
from .flb_penetrance_exporter import FLBPenetranceExporter
from .plain_penetrance_exporter import PlainPenetranceExporter

class PenetranceExporterFactory:
    """
    Factory class to create penetrance exporter instances based on specified output format.
    """

    @staticmethod
    def create_exporter(output_format, output_file):
        """
        Create a penetrance exporter based on the specified format.

        Parameters:
            output_format (str): The format of the export (e.g., "flb").
            output_file (str): Path to the output file or "stdout" for standard output.

        Returns:
            PenetranceExporter: An instance of a specific penetrance exporter.
        """
        if output_format == "flb":
            logging.debug("Creating FLBPenetranceExporter instance.")
            return FLBPenetranceExporter(output_file)
        elif output_format == "plain":
            logging.debug("Creating PlainPenetranceExporter instance.")
            return PlainPenetranceExporter(output_file)
        else:
            raise ValueError(f"Unknown penetrance export format: {output_format}")
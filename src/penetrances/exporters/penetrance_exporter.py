# src/penetrances/exporters/penetrance_exporter.py

from abc import ABC, abstractmethod

class PenetranceExporter(ABC):
    """
    Abstract base class for penetrance data exporters.
    """

    def __init__(self, output_file):
        self.output_file = output_file

    @abstractmethod
    def export_data(self, penetrance_data, liability_classes):
        """
        Abstract method to export penetrance data.

        Parameters:
            penetrance_data: The data structure with penetrance values.
            liability_classes: The mapping of individuals to liability classes.
        """
        pass
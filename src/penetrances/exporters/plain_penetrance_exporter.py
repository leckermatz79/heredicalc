# src/penetrances/exporters/plain_penetrance_exporter.py

import pandas as pd
from .penetrance_exporter import PenetranceExporter

class PlainPenetranceExporter(PenetranceExporter):
    """
    Exports penetrance data in plain text.
    """

    def export_data(self, penetrance_data, liability_classes):
        """
        Exports penetrance data in plain text.

        Parameters:
            penetrance_data (pd.DataFrame): Penetrance data with liability classes.
            liability_classes (pd.Series): Mapping of individuals to liability classes.
        """
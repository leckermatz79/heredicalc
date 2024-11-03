# src/penetrances/exporters/plain_penetrance_exporter.py

import pandas as pd
from .penetrance_exporter import PenetranceExporter

class PlainPenetranceExporter(PenetranceExporter):
    """
    Exports penetrance data in plain text.
    """

    def export_data(self, liability_classes_df):
        """
        Exports penetrance data in plain text.

        Parameters:
            liability_classes (pd.DataFrame): Penetrance data with liability classes.
        """
        pd.set_option('display.max_rows', None)
        if self.output_file == "stdout":
            print(liability_classes_df)
        else:
            # Write Data to file
            with open(self.output_file, "w") as file:
                file.write(liability_classes_df.to_string())
        pd.reset_option('display.max_rows')
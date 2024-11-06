# src/penetrances/exporters/plain_penetrance_exporter.py
import logging
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
        if self.output_file is None:
            return liability_classes_df
        elif self.output_file == "stdout":
            print(liability_classes_df)
            pd.reset_option('display.max_rows')
            return True
        else:
            try:
                liability_classes_df.to_pickle(self.output_file)
                logging.debug(f"Data successfully saved to {self.output_file}")
                pd.reset_option('display.max_rows')
                return True
            except (FileNotFoundError, IOError, OSError) as e:
                logging.error(f"Error saving data to {self.output_file}: {e}")
                pd.reset_option('display.max_rows')
                return False
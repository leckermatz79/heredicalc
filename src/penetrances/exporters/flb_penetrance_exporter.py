# src/penetrances/exporters/flb_penetrance_exporter.py

import pandas as pd
from .penetrance_exporter import PenetranceExporter

class FLBPenetranceExporter(PenetranceExporter):
    """
    Exports penetrance data to the FLB-compatible format for R.
    """

    def export_data(self, liability_classes_df):
        """
        Exports penetrance data in FLB-compatible format.

        Parameters:
            liability_classes (pd.DataFrame): Penetrance data with liability classes.
        """
        # convert penetrance data to R-Style FLB() matrix like
        penetrance_matrix = liability_classes_df.to_numpy()
        output = "penetrances = matrix(c(\n"
        output += ",\n".join(", ".join(map(str, row)) for row in penetrance_matrix)
        output += "), ncol=3, byrow=TRUE)\n\n"

        if self.output_file == "stdout":
            print(output)
        else:
            # Write Data to file
            with open(self.output_file, "w") as file:
                file.write(output)
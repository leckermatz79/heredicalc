# src/penetrances/exporters/flb_penetrance_exporter.py

import pandas as pd
from .penetrance_exporter import PenetranceExporter

class FLBPenetranceExporter(PenetranceExporter):
    """
    Exports penetrance data to the FLB-compatible format for R.
    """

    def export_data(self, penetrance_data, liability_classes):
        """
        Exports penetrance data in FLB-compatible format.

        Parameters:
            penetrance_data (pd.DataFrame): Penetrance data with liability classes.
            liability_classes (pd.Series): Mapping of individuals to liability classes.
        """
        # convert penetrance data to R-Style FLB() matrix like
        penetrance_matrix = penetrance_data.to_numpy()
        liability_vector = liability_classes.to_numpy()

        # Write Data to file
        with open(self.output_file, "w") if self.output_file != "stdout" else None as file:
            file = file or print  # Verwende print als fallback für stdout

            file.write("penetrances = matrix(c(\n")
            file.write(",\n".join(", ".join(map(str, row)) for row in penetrance_matrix))
            file.write("), ncol=3, byrow=TRUE)\n\n")

            file.write("liability = c(")
            file.write(", ".join(map(str, liability_vector)))
            file.write(")\n")
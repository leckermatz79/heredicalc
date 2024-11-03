# pedconv/exporters/cool_pedigree_exporter.py

import pandas as pd
from .pedigree_exporter import PedigreeExporter

class CoolPedigreeExporter(PedigreeExporter):
    """
    Exports pedigree data to the COOL format (Co-Segregation Online).
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def export_data(self, pedigree):
        """
        Exports pedigree data to a COOL format file.

        Parameters:
            pedigree (Pedigree): The Pedigree instance containing the data.
        """
        # Map Pedigree DataFrame to COOL-specific columns
        df = pedigree.members_df.copy()
        df = df.infer_objects()

        # Map genotype_status to COOL format symbols
        genotype_map = {
            "unk": ".",
            "neg": "Neg",
            "het": "Het",
            "hom": "Hom"
        }

        df["Geno"] = df["genotype_status"].map(genotype_map)
        # Define COOL-specific columns and handle data transformations
        export_df = pd.DataFrame({
            "PedID": ["1"] * len(df),  # Default PedID set to "1" for single pedigree
            "IndID": df["id"].astype(str).fillna("."),
            "Father": df["father_id"],
            "Mother": df["mother_id"],
            "Sex": df["gender"].fillna("."),
            "Aff": df["phenotypes"].apply(lambda ph: ph[0]["phenotype"] if ph else "."),
            "Age": df["age_last_seen"].fillna(".").astype(str),
            "Geno": df["Geno"],
            "FPTP": df["is_index_person"].apply(lambda x: 1 if x else 0)
        })



        # Replace any empty cells with the Cool-specific placeholder "."
        export_df = export_df.replace({"": "."})
        
        # Save to a tab-delimited file
        export_df.to_csv(self.file_path, sep="\t", index=False, lineterminator="\n")
# pedconv/importers/cool_pedigree_importer.py

import pandas as pd
from .pedigree_importer import PedigreeImporter

class CoolPedigreeImporter(PedigreeImporter):
    """
    Importer for the COOL pedigree format (Co-Segregation Online).
    Maps COOL-specific columns to the Pedigree data structure.
    """
    
    def __init__(self, file_path):
        self.file_path = file_path

    def import_data(self, pedigree):
        """
        Reads the COOL file and adds individuals to the Pedigree.
        
        Parameters:
            pedigree (Pedigree): The Pedigree instance to populate with imported data.
        """
        df = pd.read_csv(self.file_path, sep="\t")
        
        for _, row in df.iterrows():
            # Map COOL columns to Pedigree structure
            genotype_status = {
                ".": "unk",
                "0": "unk",
                "Neg": "neg",
                "Het": "het",
                "Hom": "hom"
            }.get(row["Geno"], "unk")

            pedigree.add_member(
                id=row["IndID"],
                pseudonym=str(row["IndID"]),  # Use IndID as pseudonym initially
                father_id=row["Father"],
                mother_id=row["Mother"],
                gender= row["Sex"],
                phenotypes=[] if row["Aff"]=="." else [{"phenotype": row["Aff"], "age": row["Age"]}],
                age_last_seen=row["Age"],
                death_age=None,
                is_index_person = (row["FPTP"] == 1),
                genotype_status=genotype_status  
            )
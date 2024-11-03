# pedconv/exporters/segregatr_flb_pedigree_exporter.py

import pandas as pd
from .pedigree_exporter import PedigreeExporter

class SegregatrFLBPedigreeExporter(PedigreeExporter):
    """
    Exports pedigree data to the segregatr FLB format for R.
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def export_data(self, pedigree):
        """
        Exports pedigree data to a segregatr FLB-compatible format in R.

        Parameters:
            pedigree (Pedigree): The Pedigree instance containing the data.
        """  
        df = pedigree.members_df.copy()
        df = df.infer_objects()

        # Map gender to R format (1 = M, 2 = F)
        df["sex"] = df["gender"].map({"M": 1, "F": 2}).fillna("NA")

        # Convert genotype_status into R vectors for carriers, homozygous, and noncarriers
        carriers = df[df["genotype_status"] == "het"]["id"].tolist()
        homozygous = df[df["genotype_status"] == "hom"]["id"].tolist()
        noncarriers = df[df["genotype_status"] == "neg"]["id"].tolist()

        # Get proband ID (Indexperson) if available
        proband_id = df[df["is_index_person"] == True]["id"].iloc[0] if any(df["is_index_person"]) else "NA"

        # Determine affected and unknown based on phenotypes list
        affected = df[df['phenotypes'].apply(lambda x: bool(x) and any(p.get("phenotype") != "unaff" for p in x))]["id"].astype(str).tolist()
        unknown = df[df['phenotypes'].apply(lambda x: not x)]["id"].astype(str).tolist()

        # Create vectors in R format for each column needed by segregatr
        id_vector = ", ".join(df["id"].astype(str).fillna("NA"))
        fid_vector = ", ".join(df["father_id"].fillna(0).astype(int).astype(str))
        mid_vector = ", ".join(df["mother_id"].fillna(0).astype(int).astype(str))
        sex_vector = ", ".join(df["sex"].astype(str))

        # Write the data to an .R file in the expected vector format
        with open(self.file_path, "w") as file:
            file.write("ped <- ped(\n")
            file.write(f"  id = c({id_vector}),\n")
            file.write(f"  fid = c({fid_vector}),\n")
            file.write(f"  mid = c({mid_vector}),\n")
            file.write(f"  sex = c({sex_vector}),\n")
            file.write('  famid = "",\n')
            file.write("  reorder = TRUE,\n")
            file.write("  validate = TRUE,\n")
            file.write("  detectLoops = TRUE,\n")
            file.write("  isConnected = FALSE,\n")
            file.write("  verbose = FALSE\n")
            file.write(")\n\n")

            # Write the genotype status vectors for carriers, homozygous, and noncarriers
            file.write("# Genotype-specific vectors\n")
            file.write(f"carriers <- c({', '.join(map(str, carriers))})\n")
            file.write(f"homozygous <- c({', '.join(map(str, homozygous))})\n")
            file.write(f"noncarriers <- c({', '.join(map(str, noncarriers))})\n")

            file.write(f"affected <- c({', '.join(affected)})\n")
            file.write(f"unknown <- c({', '.join(unknown)})\n")

            # Add proband ID (Indexperson)
            file.write(f"proband <- {proband_id}\n")

            # Example FLB function call setup
            #file.write("FLB(ped, proband=proband)\n")            
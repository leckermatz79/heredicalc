# pedconv/exporters/segregatr_flb_pedigree_exporter.py

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
        df = pedigree.copy()
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

        export_str = "ped <- ped(\n"
        export_str += f"  id = c({id_vector}),\n"
        export_str += f"  fid = c({fid_vector}),\n"
        export_str += f"  mid = c({mid_vector}),\n"
        export_str += f"  sex = c({sex_vector}),\n"
        export_str += '  famid = "",\n'
        export_str += "  reorder = TRUE,\n"
        export_str += "  validate = TRUE,\n"
        export_str += "  detectLoops = TRUE,\n"
        export_str += "  isConnected = FALSE,\n"
        export_str += "  verbose = FALSE\n"
        export_str += ")\n\n"

        # Write the genotype status vectors for carriers, homozygous, and noncarriers
        export_str += "# Genotype-specific vectors\n"
        export_str += f"carriers <- c({', '.join(map(str, carriers))})\n"
        export_str += f"homozygous <- c({', '.join(map(str, homozygous))})\n"
        export_str += f"noncarriers <- c({', '.join(map(str, noncarriers))})\n"

        export_str += f"affected <- c({', '.join(affected)})\n"
        export_str += f"unknown <- c({', '.join(unknown)})\n"

        # Add proband ID (Indexperson)
        export_str += f"proband <- {proband_id}\n"
        
        if self.file_path is None:
            return export_str
        elif self.file_path == "stdout":
            print(export_str)
        else:
            # Write the data to an .R file in the expected vector format
            with open(self.file_path, "w") as file:
                file.write(export_str)
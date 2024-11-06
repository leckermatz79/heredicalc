# pedconv/importers/cool_pedigree_importer.py

import pandas as pd
from .pedigree_importer import PedigreeImporter

class CoolPedigreeImporter(PedigreeImporter):
    """
    Importer for the COOL pedigree format (Co-Segregation Online).
    Maps COOL-specific columns to the Pedigree data structure.
    """
    def __init__(self, file_path):
        self.COOL_MAPPINGS = {
            'unaff': 'Unaffected', 
            'Lip': None, 
            'Tongue': None, 
            'Mouth': None, 
            'Oral': None, 
            'Saliv': None, 
            'Parotid': None, 
            'Tonsil': None, 
            'Oroph': None, 
            'Nasoph': None, 
            'Pyrifm': None, 
            'Hypoph': None, 
            'Pharynx': None, 
            'BCP': None, 
            'Throat': None, 
            'Nasal': None, 
            'A.sinus': None, 
            'Larynx': None, 
            'Trachea': None, 
            'Oesoph': 'EsophagealCancer', 
            'Stomach': 'StomachCancer', 
            'SmBowel': None, 
            'Colon': 'ColorectalCancer', 
            'RS.junc': 'ColorectalCancer', 
            'Rectum': 'ColorectalCancer', 
            'CRC': 'ColorectalCancer', 
            'Anus': None, 
            'Liver': 'LiverCancer', 
            'Gall': None, 
            'Biliary': None, 
            'PanCa': 'PancreaticCancer', 
            'SSBP': None, 
            'BilPan': None, 
            'Lung': 'LungCancer', 
            'Thymus': None, 
            'Heart': None, 
            'Bone': None, 
            'Bone.l': None, 
            'Bone.o': None, 
            'Osteo': None, 
            'Sarcoma': None, 
            'CM': 'Melanoma', 
            'NM.skin': None, 
            'Meso': None, 
            'STS': None, 
            'BrCa': 'BreastCancer', 
            'Vagina': None, 
            'Cervix': 'CervicalCancer', 
            'Corpus': 'EndometrialCancer', 
            'Uterus': 'UterineCancer', 
            'OvCa': 'OvarianCancer', 
            'Penis': None, 
            'ProCa': 'ProstateCancer', 
            'Testis': None, 
            'UpUrin': None, 
            'Kidney': 'KidneyCancer', 
            'RenalCC': 'KidneyCancer', 
            'RCC': 'KidneyCancer', 
            'Ureter': None, 
            'Bladder': 'BladderCancer', 
            'Urinary': None, 
            'Eye': None, 
            'UM': None, 
            'Mening': None, 
            'CNS': None, 
            'Brain': None, 
            'Thyroid': 'ThyroidCancer', 
            'MTC': None, 
            'Adrenal': None, 
            'Hodgkin': None, 
            'NH.lym': 'NonHodgkinLymphoma', 
            'IPD': None, 
            'Myeloma': None, 
            'L.leuk': 'Leukemia', 
            'M.leuk': 'Leukemia', 
            'U.leuk': 'Leukemia', 
            'Leuk': 'Leukemia', 
            'Lymph': None, 
            "." : "Unknown" 
        }
        self.file_path = file_path

    def import_data(self, pedigree):
        """
        Reads the COOL file and adds individuals to the Pedigree.
        
        Parameters:
            pedigree (Pedigree): The Pedigree instance to populate with imported data.
        """
        df = pd.read_csv(self.file_path, sep="\t")
        phenos = []
        
        for _, row in df.iterrows():
            # Map COOL columns to Pedigree structure
            genotype_status = {
                ".": "unk",
                "0": "unk",
                "Neg": "neg",
                "Het": "het",
                "Hom": "hom"
            }.get(row["Geno"], "unk")

            if row["Aff"] not in (".", 0):
                phenotype_name = self.COOL_MAPPINGS.get(row["Aff"], None)
                phenos = [{"phenotype": phenotype_name}]
            else: 
                phenos = [{"phenotype": "Unknown"}]

            pedigree.add_member(
                id=row["IndID"],
                pseudonym=str(row["IndID"]),  # Use IndID as pseudonym initially
                father_id=row["Father"],
                mother_id=row["Mother"],
                gender= row["Sex"],
                phenotypes= phenos,
                age_last_seen=row["Age"],
                death_age=None,
                is_index_person = (row["FPTP"] == 1),
                genotype_status=genotype_status  
            )
# pedconv/pedigree.py
import pandas as pd

class Pedigree:
    def __init__(self):
        self.members_df = pd.DataFrame(columns=[
            'id', 'pseudonym', 'father_id', 'mother_id', 'gender',
            'phenotypes', 'age_last_seen', 'death_age', 'is_index_person', 'genotype_status'
        ])

    def add_member(self, id, pseudonym, father_id, mother_id, gender, phenotypes=None, age_last_seen=None, death_age=None, is_index_person=False, genotype_status="unk"):
        # Ensure correct data types for specific columns
        id = int(id) if pd.notna(id) else None
        father_id = int(father_id) if pd.notna(father_id) else None
        mother_id = int(mother_id) if pd.notna(mother_id) else None
        
        member_data = {
            'id': id,
            'pseudonym': pseudonym,
            'father_id': father_id,
            'mother_id': mother_id,
            'gender': gender,
            'phenotypes': phenotypes or [],
            'age_last_seen': age_last_seen,
            'death_age': death_age,
            'is_index_person': is_index_person,
            'genotype_status': genotype_status 
        }
        
        new_row = pd.DataFrame([member_data])
        self.members_df = pd.concat([self.members_df, new_row], ignore_index=True)
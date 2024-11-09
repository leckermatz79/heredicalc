import pandas as pd
import logging
import sys

def map_liabilities(liabilities_df, pedigree_df):
    """
    Maps liability classes to individuals in the pedigree based on gender, age, and phenotype,
    and returns a vector with the row numbers of penetrances for each individual.

    Parameters:
    liabilities_file (str): Path to the CSV file containing liability data.
    pedigree_file (str): Path to the pedigree file, typically with IDs, gender, age, and phenotype information.

    Returns:
    str: A string representing a numeric vector of liability classes for each individual in the pedigree.
    """
    
    # Load liabilities and pedigree data
    #liabilities_df = pd.read_pickle(liabilities_file)
    #pedigree_df = pd.read_csv(pedigree_file, delim_whitespace=True)
    
    # Ensure the pedigree data is sorted by 'id'
    pedigree_df = pedigree_df.sort_values(by='id').reset_index(drop=True)
    logging.debug(pedigree_df)
    logging.debug ("***")
    logging.debug(liabilities_df)
    #sys.exit(0)
    # List to store the liability class index for each individual
    liability_vector = []

    # Iterate over each individual in the pedigree, sorted by 'id'
    for _, ped_row in pedigree_df.iterrows():
        # Extract relevant attributes for matching
        ped_gender = ped_row['gender']
        logging.debug(f"ped_gender: {ped_gender}, ped_row_gender:{ped_row['gender']}")
        ped_age = ped_row['age_last_seen']
        logging.debug(f"ped_age: {ped_age}, ped_row_age_last_seen:{ped_row['age_last_seen']}")
        # Treat Unkonwn phenotype as Unaffected for liability class mapping
        logging.debug(f"phenotypes: {ped_row['phenotypes'][0]}")
        if ped_row['phenotypes'] and ped_row['phenotypes'][0].get('phenotype') != "Unknown":
            ped_phenotype = ped_row['phenotypes'][0].get("phenotype", "Unaffected")
        else:
            ped_phenotype = "Unaffected"
        logging.debug(f"ped_phenotype: {ped_phenotype}, ped_row['phenotypes'][0]: {ped_row['phenotypes'][0].get('phenotype', 'Unaffected')}")
        #ped_phenotype = "Unaffected" if ped_row['phenotypes'][0].get == "Unknown"
        #logging.debug(f"ped_phenotype: {ped_phenotype}")

        # Filter liabilities to match the individual's gender and phenotype
        matching_liabilities = liabilities_df[
            (liabilities_df['gender'] == ped_gender) &
            (liabilities_df['phenotype'] == ped_phenotype)
        ]


        # Find the matching liability class based on age range
        matched_liability = matching_liabilities[
            (matching_liabilities['age_class_lower'] <= ped_age) &
            (matching_liabilities['age_class_upper'] >= ped_age)
        ]        
        logging.debug ("Matching liabilities - age class:")
        logging.debug(matched_liability)
        #sys.exit(0)
        # Append the row number (1-based index) of the matched liability class or default to 1
        if not matched_liability.empty:
            liability_class_index = matched_liability.index[0] + 1 # (accounting for 1-based liability vector)
        else:
            logging.critical("No matching liability class found! defaulting to 1.")
            liability_class_index = 1  # Default to 1 if no match is found

        liability_vector.append(liability_class_index)

    # Convert the liability vector to a string format suitable for R
    liability_str = "liability <- c(" + ", ".join(map(str, liability_vector)) + ")"
    logging.debug(liability_str)
    #sys.exit(0)
    return liability_str
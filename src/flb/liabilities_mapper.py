import pandas as pd

def map_liabilities(liabilities_file, pedigree_file):
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
    liabilities_df = pd.read_csv(liabilities_file)
    pedigree_df = pd.read_csv(pedigree_file, delim_whitespace=True)
    
    # Ensure the pedigree data is sorted by 'id'
    pedigree_df = pedigree_df.sort_values(by='id').reset_index(drop=True)

    # List to store the liability class index for each individual
    liability_vector = []

    # Iterate over each individual in the pedigree, sorted by 'id'
    for _, ped_row in pedigree_df.iterrows():
        # Extract relevant attributes for matching
        ped_gender = ped_row['gender']
        ped_age = ped_row['age']
        ped_phenotype = ped_row['phenotype']

        # Filter liabilities to match the individual's gender and phenotype
        matching_liabilities = liabilities_df[
            (liabilities_df['gender'] == ped_gender) &
            (liabilities_df['phenotype'] == ped_phenotype)
        ]

        # Find the matching liability class based on age range
        matched_liability = matching_liabilities[
            (matching_liabilities['age_min'] <= ped_age) &
            (matching_liabilities['age_max'] >= ped_age)
        ]

        # Append the row number (1-based index) of the matched liability class or default to 1
        if not matched_liability.empty:
            liability_class_index = matched_liability.index[0] + 1  # Convert to 1-based index
        else:
            liability_class_index = 1  # Default to 1 if no match is found

        liability_vector.append(liability_class_index)

    # Convert the liability vector to a string format suitable for R
    liability_str = "c(" + ", ".join(map(str, liability_vector)) + ")"
    
    return liability_str
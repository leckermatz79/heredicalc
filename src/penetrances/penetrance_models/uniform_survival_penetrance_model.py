# penetrances/penetrance_models/uniform_survival_penetrance_model.py

import logging
from .penetrance_model import PenetranceModel

class UniformSurvivalPenetranceModel(PenetranceModel):
    """
    Uniform Survival Penetrance Model calculates penetrance by assuming that carriers and non-carriers
    have survived to the current age class if they have not been affected in prior age classes.
    """
    
    def calculate_penetrance(self, liability_classes_df, cumulative_risk_df):
        """
        Calculate the penetrance values for non-carriers, heterozygotes, and homozygotes
        in each age class by applying the survival model.

        Parameters:
            liability_classes_df (pd.DataFrame): DataFrame containing liability class details
            cumulative_risk_df (pd.DataFrame): DataFrame containing cumulative risks by age class
        
        Returns:
            pd.DataFrame: Updated liability_classes_df with penetrance values.
        """
        
        # Loop over each row in liability_classes_df to calculate penetrance
        for idx, row in liability_classes_df.iterrows():
            age_lower = row['age_class_lower']
            age_upper = row['age_class_upper']
            gender = row['gender']
            
            # Check if there's a previous age class
            if age_lower == 0:
                # No prior age class, use lambda values directly for the first age class
                liability_classes_df.at[idx, 'penetrance_nc'] = row['lambda_nc']
                liability_classes_df.at[idx, 'penetrance_het'] = row['lambda_het']
                liability_classes_df.at[idx, 'penetrance_hom'] = row['lambda_hom']
                logging.debug(f"Initial age class for gender={gender}, age_upper={age_upper}: "
                              f"Penetrance NC={row['lambda_nc']}, HET={row['lambda_het']}, HOM={row['lambda_hom']}")
            else:
                # Get cumulative risk of previous age class
                prev_row = cumulative_risk_df[
                    (cumulative_risk_df['gender'] == gender) &
                    (cumulative_risk_df['age_class_upper'] == (age_lower-1))
                ]
                
                if not prev_row.empty:
                    cr_nc = prev_row.iloc[0]['cr_nc']
                    cr_het = prev_row.iloc[0]['cr_het']
                    cr_hom = prev_row.iloc[0]['cr_hom']
                    
                    # Calculate penetrance using survival model assumption
                    liability_classes_df.at[idx, 'penetrance_nc'] = row['lambda_nc'] * (1 - cr_nc)
                    liability_classes_df.at[idx, 'penetrance_het'] = row['lambda_het'] * (1 - cr_het)
                    liability_classes_df.at[idx, 'penetrance_hom'] = row['lambda_hom'] * (1 - cr_hom)

                    logging.debug(f"Gender={gender}, age_upper={age_upper}: "
                                  f"Penetrance NC={liability_classes_df.at[idx, 'penetrance_nc']}, "
                                  f"HET={liability_classes_df.at[idx, 'penetrance_het']}, "
                                  f"HOM={liability_classes_df.at[idx, 'penetrance_hom']}")
                else:
                    logging.warning(f"No previous age class found for gender={gender}, age_upper={age_upper}")
        
        return liability_classes_df
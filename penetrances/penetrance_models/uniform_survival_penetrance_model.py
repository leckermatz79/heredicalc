# V3/penetrances/penetrance_models/uniform_survival_penetrance_model.py

import logging
from V3.penetrances.penetrance_models.penetrance_model import PenetranceModel

class UniformSurvivalPenetranceModel(PenetranceModel):
    """
    Uniform Survival Penetrance Model for calculating penetrance values
    based on CRHF, relative risks, and incidence rates.
    """
    
    def calculate_penetrance(self, gene, phenotype, cumulative_risk, incidence_rate, crhf, rr_het, rr_hom, gender, age_class_upper):
        """
        Calculate penetrance values for non-carriers, heterozygous, and homozygous carriers.
        
        Parameters:
            gene (str): Gene symbol.
            phenotype (str): Phenotype being calculated.
            cumulative_risk (float): Cumulative risk up to the previous age class.
            incidence_rate (float): Incidence rate for the current age class.
            crhf (float): CRHF value for the gene and age class.
            rr_het (float): Relative risk for heterozygous carriers.
            rr_hom (float): Relative risk for homozygous carriers.
            gender (str): Gender of the individual.
            age_class_upper (float): Upper limit of the age class.
        
        Returns:
            tuple: Penetrance values for non-carriers, heterozygous carriers, and homozygous carriers.
        """
        
        logging.debug(f"Calculating penetrance for gene: {gene}, phenotype: {phenotype}, "
                      f"gender: {gender}, age_class_upper: {age_class_upper}, "
                      f"cumulative_risk: {cumulative_risk}, incidence_rate: {incidence_rate}, "
                      f"crhf: {crhf}, rr_het: {rr_het}, rr_hom: {rr_hom}")
        
        # Hier kann später die eigentliche Berechnung implementiert werden
        # Diese Platzhalter-Rückgabe dient zur Überprüfung der Eingangsparameter
        return cumulative_risk, incidence_rate * rr_het, incidence_rate * rr_hom
# V3/penetrances/penetrance_models.py
import logging
from abc import ABC, abstractmethod
from V3.penetrances.relative_risk.relative_risk_models import RelativeRiskModel
from V3.penetrances.crhf_models import CRHFModel

class PenetranceModel(ABC):
    """
    Abstract base class for calculating penetrance.
    """
    def __init__(self, incidence_data, relative_risk_model: RelativeRiskModel, crhf_model: CRHFModel):
        self.incidence_data = incidence_data
        self.relative_risk_model = relative_risk_model
        self.crhf_model = crhf_model
        logging.debug("Initialized PenetranceModel with incidence data and models.")

    @abstractmethod
    def calculate_penetrance(self, gene, phenotype):
        """
        Abstract method to calculate penetrance for a given gene and phenotype.
        
        Raises:
            NotImplementedError: Must be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class UniformPenetranceModel(PenetranceModel):
    """
    Uniform Penetrance Model that assumes a uniform distribution of incidence within age groups.
    """
    def calculate_penetrance(self, gene, phenotype):
        """
        Calculate the penetrance assuming a uniform distribution across age groups.

        Parameters:
            gene (str): Gene symbol (e.g., "BRCA1").
            phenotype (str): Phenotype (e.g., "BreastCancer").

        Returns:
            dict: Penetrance values by age group for both heterozygous and homozygous carriers.
        """
        penetrance_results = []
        crhf = self.crhf_model.get_crhf(gene)

        for _, row in self.incidence_data.iterrows():
            age = row["age_class_lower"]
            gender = row["gender"]
            base_incidence = row["cases"] / row["person_years"]
            
            # Get relative risks for the specified phenotype and gender
            hetero_rr, homo_rr = self.relative_risk_model.get_relative_risk(age, phenotype, gender)

            # Calculate penetrance values
            hetero_penetrance = base_incidence * hetero_rr * crhf
            homo_penetrance = base_incidence * homo_rr * crhf**2

            penetrance_results.append({
                "age_class": row["age_class_lower"],
                "gender": gender,
                "phenotype": phenotype,
                "heterozygous_penetrance": hetero_penetrance,
                "homozygous_penetrance": homo_penetrance
            })

        logging.info(f"Penetrance for {gene} and {phenotype} calculated successfully.")
        return penetrance_results
# V3/penetrances/penetrance_models.py
import logging
from abc import ABC, abstractmethod
from V3.penetrances.relative_risk.relative_risk_models import RelativeRiskModel
from V3.penetrances.crhf_models import CRHFModel
import pandas as pd


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
        Calculate penetrance based on a uniform model where cases are distributed
        evenly across years within age groups.
        
        Parameters:
            gene (str): The gene for which to calculate penetrance.
            phenotype (str): The phenotype associated with the gene.
        
        Returns:
            pd.DataFrame: DataFrame containing penetrance information with columns
            such as ['age_group', 'gender', 'heterozygous_penetrance', 'homozygous_penetrance'].
        """
        penetrance_data = []

        for _, row in self.incidence_data.iterrows():
            age_lower = row["age_class_lower"]
            age_upper = row["age_class_upper"]
            age_range = age_upper - age_lower if age_upper else 1  # Avoid division by zero
            
            # Fetch CRHF and relative risks
            crhf = self.crhf_model.get_crhf(gene)
            hetero_rr, homo_rr = self.relative_risk_model.get_relative_risk(age_lower, phenotype, row["gender"])

            # Calculate penetrance for heterozygous and homozygous cases
            heterozygous_penetrance = (row["cases"] * hetero_rr * crhf) / (row["person_years"] * age_range)
            homozygous_penetrance = (row["cases"] * homo_rr * crhf**2) / (row["person_years"] * age_range)
            
            penetrance_data.append({
                "age_group": f"{age_lower}-{age_upper}" if age_upper else f"{age_lower}+",
                "gender": row["gender"],
                "heterozygous_penetrance": heterozygous_penetrance,
                "homozygous_penetrance": homozygous_penetrance,
                "phenotype": phenotype,
                "gene": gene
            })
        
        # Convert list of dictionaries to DataFrame
        return pd.DataFrame(penetrance_data)
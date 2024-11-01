# V3/penetrances/penetrance_models/penetrance_model_factory.py
import logging
from .penetrance_models import PenetranceModel
from .penetrance_models import UniformPenetranceModel
from V3.penetrances.relative_risk.relative_risk_models import RelativeRiskModel
from V3.penetrances.crhf_models import CRHFModel

class PenetranceModelFactory:
    """
    Factory class to create different penetrance models.
    """
    @staticmethod
    def create_penetrance_model(model_type, incidence_data, relative_risk_model: RelativeRiskModel, crhf_model: CRHFModel):
        """
        Create a penetrance model based on the specified type.

        Parameters:
            model_type (str): The type of penetrance model (e.g., "uniform").
            incidence_data (pd.DataFrame): Incidence data as a DataFrame.
            relative_risk_model (RelativeRiskModel): The relative risk model instance.
            crhf_model (CRHFModel): The CRHF model instance.

        Returns:
            PenetranceModel: An instance of a specific penetrance model.
        """
        if model_type == "uniform":
            logging.debug("Creating UniformPenetranceModel instance.")
            return UniformPenetranceModel(incidence_data, relative_risk_model, crhf_model)
        else:
            raise ValueError(f"Unknown penetrance model type: {model_type}")    
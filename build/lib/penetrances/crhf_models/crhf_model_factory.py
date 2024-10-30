# V3/penetrances/crhf_models/crhf_model_factory.py
import logging
from .constant_crhf_model import ConstantCRHFModel

class CRHFModelFactory:
    """Factory to create CRHF model instances."""

    @staticmethod
    def create_model(model_name="constant"):
        if model_name == "constant":
            return ConstantCRHFModel()
        else:
            raise ValueError(f"CRHF model '{model_name}' is not implemented.")
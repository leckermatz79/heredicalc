penetrances/penetrance_models/penetrance_model_factory.py
import logging
from .uniform_penetrance_model import UniformPenetranceModel
from .uniform_survival_penetrance_model import UniformSurvivalPenetranceModel
from .dummy_penetrance_model import DummyPenetranceModel

class PenetranceModelFactory:
    """
    Factory class to create different penetrance models.
    """
    @staticmethod
    def create_model(model_type, *args, **kwargs):
        """
        Create a penetrance model based on the specified type.

        Parameters:
            model_type (str): The type of penetrance model (e.g., "uniform_survival").
            *args: Positional arguments to be passed to the model.
            **kwargs: Keyword arguments to be passed to the model.

        Returns:
            PenetranceModel: An instance of a specific penetrance model.

        Raises:
            ValueError: If the specified model type is not supported.
        """
        if model_type == "uniform":
            logging.debug("Creating UniformPenetranceModel instance.")
            return UniformPenetranceModel(*args, **kwargs)
        elif model_type == "uniform_survival":
            logging.debug("Creating UniformSurvivalPenetranceModel instance.")
            return UniformSurvivalPenetranceModel(*args, **kwargs)
        elif model_type == "dummy":
            logging.debug("Creating DummyPenetranceModel instance.")
            return DummyPenetranceModel(*args, **kwargs)
        else:
            raise ValueError(f"Unknown penetrance model type: {model_type}")    
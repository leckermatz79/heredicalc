# incidences/incidence_models/incidence_data_model_factory.py
import logging
from .ci5_detailed_incidence_model import CI5DetailedIncidenceModel
from .ci5_summary_incidence_model import CI5SummaryIncidenceModel
from .incidence_data_model import IncidenceDataModel

class IncidenceDataModelFactory:
    """Factory for creating data parsers based on dataset type."""

    @staticmethod
    def create_incidence_model(source_config, population=None):
        incidence_model_type = source_config.get("parser")
        
        if incidence_model_type == "ci5_detailed_incidence_model":
            return CI5DetailedIncidenceModel(source_config, population)
        elif incidence_model_type == "ci5_summary_incidence_model":
            return CI5SummaryIncidenceModel(source_config, population)
        else:
            logging.error(f"Unknown incidence model type: {incidence_model_type}")
            raise ValueError(f"Unsupported incidence model: {incidence_model_type}")
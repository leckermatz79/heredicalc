penetrances/crhf_models/crhf_model_factory.py

from .constant_crhf_model import ConstantCRHFModel

class CRHFModelFactory:
    """Factory to create CRHF model instances."""

    @staticmethod
    def create_model(model_name="constant", gene=None, data_frame=None, crhf_file_path=None):
        """
        Create a CRHF model instance based on the specified model name.

        Parameters:
            model_name (str): The name of the CRHF model type (default: "constant").
            gene (str): The gene symbol to use for CRHF calculation.
            data_frame (pd.DataFrame): DataFrame containing relevant data for CRHF calculation.
            crhf_file_path (str): Optional path to the CRHF values file (for constant model).

        Returns:
            CRHFModel: An instance of a CRHF model.
        """
        if model_name == "constant":
            if gene is None or data_frame is None:
                raise ValueError("Gene and data_frame must be provided for the constant CRHF model.")
            return ConstantCRHFModel(gene, data_frame, crhf_file_path)
        else:
            raise ValueError(f"CRHF model '{model_name}' is not implemented.")
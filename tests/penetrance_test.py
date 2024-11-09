penetrances/penetrance_test.py
import logging
import pandas as pd
from heredicalc.penetrances.penetrance_model_factory import PenetranceModelFactory
from heredicalc.penetrances.relative_risk.static_lookup_rr_model import StaticLookupRRModel
from heredicalc.penetrances.crhf_models import ConstantCRHFModel

# Set up logging to display debug information
logging.basicConfig(level=logging.DEBUG)

def test_uniform_penetrance_model():
    # Simulated incidence data as a DataFrame for testing
    incidence_data = pd.DataFrame({
        "age_class_lower": [0, 50, 70],
        "age_class_upper": [49, 69, None],
        "cases": [100, 150, 200],
        "person_years": [10000, 12000, 14000],
        "phenotype": ["BreastCancer"] * 3,
        "gender": ["F", "F", "F"]
    })

    # Create CRHF and RelativeRisk model instances
    crhf_model = ConstantCRHFModel()
    rr_model = StaticLookupRRModel("BRCA1")  # Assuming BRCA1 data is available

    print(incidence_data)

    # Create the penetrance model using the factory
    model_type = "uniform"
    penetrance_model = PenetranceModelFactory.create_penetrance_model(model_type, incidence_data, rr_model, crhf_model)

    # Define test parameters
    gene = "BRCA1"
    phenotype = "BreastCancer"
    test_ages = [25, 55, 75]  # Various age points to test boundaries

    print("Testing UniformPenetranceModel with various ages:")
    penetrance = penetrance_model.calculate_penetrance(gene, phenotype)
    print (penetrance)

if __name__ == "__main__":
    test_uniform_penetrance_model()
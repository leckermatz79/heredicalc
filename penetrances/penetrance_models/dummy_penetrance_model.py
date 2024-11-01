# V3/penetrances/penetrance_models/dummy_penetrance_model.py

from V3.penetrances.penetrance_models.penetrance_model import PenetranceModel
from V3.penetrances.relative_risk_models.relative_risk_model import RelativeRiskModel
from V3.penetrances.crhf_models.crhf_model import CRHFModel

class DummyPenetranceModel(PenetranceModel):
    
    def calculate_penetrance(self, cumulative_risk, crhf_value, rr_het, rr_hom):
        return 1.0, 2.0, 3.0
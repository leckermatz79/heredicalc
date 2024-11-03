# V3/penetrances/penetrance_models/dummy_penetrance_model.py

from .penetrance_model import PenetranceModel

class DummyPenetranceModel(PenetranceModel):
    
    def calculate_penetrance(self, cumulative_risk, crhf_value, rr_het, rr_hom):
        return 1.0, 2.0, 3.0
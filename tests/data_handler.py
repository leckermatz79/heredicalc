import yaml
import logging
from datetime import datetime
import argparse
from V3.core.setup_logging import setup_logging
from V3.penetrances.crhf_models import CRHFModelFactory 

def main():
    logging.info ("penetrance data handler called succesfully.")
    crhf_model = CRHFModelFactory.create_model("constant")
    print(crhf_model.get_crhf("BRCA1"))  # Expected: 0.00075
    print(crhf_model.get_crhf("BRCA2"))  # Expected: 0.0013
    print(crhf_model.get_crhf("TP53"))   # Expected: None or Error message (still to be implemented)
if (__name__ == "__main__"):
    main()
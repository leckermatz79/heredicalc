# V3/bin/crhf.py
import argparse
import logging
from V3.core.setup_logging import setup_logging
from V3.penetrances.crhf_models.crhf_model_factory import CRHFModelFactory

def parse_arguments():
    parser = argparse.ArgumentParser(description="Retrieve CRHF values for a specified gene.")
    parser.add_argument("--crhftype", required=True, help="Specify the CRHF model to use (e.g., 'constant').")
    parser.add_argument("--gene", required=True, help="Specify the gene symbol to retrieve CRHF (e.g., 'BRCA1').")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "SILENT"],
                        help="Set the logging level.")
    return parser.parse_args()

def main():
    args = parse_arguments()
    setup_logging(args.log_level)

    try:
        # Instantiate the CRHF model via factory
        crhf_model = CRHFModelFactory.create_model(args.crhftype)
        # Retrieve CRHF for the specified gene
        crhf_value = crhf_model.get_crhf(args.gene)

        if crhf_value is not None:
            print(f"CRHF for {args.gene} using '{args.crhftype}' model: {crhf_value}")
        else:
            print(f"CRHF value for gene '{args.gene}' not found in '{args.crhftype}' model.")
            logging.warning(f"CRHF value for gene '{args.gene}' not found in model '{args.crhftype}'.")

    except Exception as e:
        logging.error(f"Error retrieving CRHF value: {e}")

if __name__ == "__main__":
    main()
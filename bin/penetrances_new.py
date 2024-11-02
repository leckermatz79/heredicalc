# V3/bin/penetrances_new.py

import argparse
import os
import logging
import pandas as pd
import yaml
from V3.core.setup_logging import setup_logging
from V3.incidences.incidence_data_source_handlers.data_source_handler_factory import DataSourceHandlerFactory
from V3.incidences.incidence_models.incidence_data_model_factory import IncidenceDataModelFactory
from V3.penetrances.crhf_models.crhf_model_factory import CRHFModelFactory

def parse_arguments():
    parser = argparse.ArgumentParser(description="Initialize central data structure for penetrance calculations.")
    parser.add_argument("--dataset", required=True, help="Specify the dataset (e.g., ci5_ix)")
    parser.add_argument("--population", help="Specify the population by key number (e.g., 38402499)")
    parser.add_argument("--phenotypes", nargs='+', required=True, help="Specify phenotypes to include (e.g., BreastCancer OvarianCancer)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "SILENT"],
                        help="Set the logging level")
    parser.add_argument("--force-download", action="store_true", help="Force data re-download if necessary")
    parser.add_argument("--crhf_model", default="constant", help="Specify the CRHF model to use (default: constant)")
    parser.add_argument("--gene", required=True, help="Specify the gene for CRHF calculation")
    return parser.parse_args()

def load_sources():
    """Load the sources.yaml configuration file for dataset information."""
    sources_path = os.path.join(os.path.dirname(__file__), "../data_sources/incidences/sources.yaml")
    with open(sources_path, "r") as f:
        return yaml.safe_load(f)

def main():
    args = parse_arguments()
    setup_logging(args.log_level)
    
    # Load dataset configuration
    sources = load_sources()["sources"]
    if args.dataset not in sources:
        logging.error(f"Dataset '{args.dataset}' not found in sources.yaml.")
        return

    source_config = sources[args.dataset]
    data_handler = DataSourceHandlerFactory.create_data_source_handler(source_config, force_download=args.force_download)
    data_handler.handle_data()

    # Load and process incidence data
    data_parser = IncidenceDataModelFactory.create_incidence_model(source_config, population=args.population)
    df = data_parser.parse_data()  # Load the data
    df = data_parser.filter_by_phenotypes(df, args.phenotypes)  # Filter by selected phenotypes
    df = data_parser.build_incidence_table(df)  # Standardize to incidence table structure
    df = data_parser.add_age_span_column(df)  # Add age span (age_class_upper - age_class_lower)
    df = data_parser.add_incidence_rate_column()  # Calculate incidence rates

    # Initial structure of the central DataFrame
    central_df = df[["gender", "age_class_lower", "age_class_upper", "age_span", "phenotype", "incidence_rate"]].copy()
    
    # Initialize CRHF model based on the CLI parameter
    crhf_model = CRHFModelFactory.create_model(args.crhf_model, gene=args.gene, data_frame=central_df)

    # Calculate CRHF values for each row and add them to a new 'crhf' column
    central_df["crhf"] = central_df.apply(
        lambda row: crhf_model.calculate_crhf(row["gender"], row["age_class_upper"]), axis=1
    )

    # Log the central DataFrame with CRHF values
    logging.info(f"Central DataFrame with CRHF values:\n{central_df.head()}")

    # Output the central DataFrame for checking purposes
    print("Central DataFrame with CRHF values:")
    print(central_df)

if __name__ == "__main__":
    main()
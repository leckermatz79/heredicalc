# bin/crhf.py
import argparse
import logging
import pandas as pd
from heredicalc.core.setup_logging import setup_logging
from heredicalc.incidences.incidence_data_source_handlers.data_source_handler_factory import DataSourceHandlerFactory
from heredicalc.incidences.incidence_models.incidence_data_model_factory import IncidenceDataModelFactory
from heredicalc.penetrances.crhf_models.crhf_model_factory import CRHFModelFactory
from heredicalc.core.setup_data_sources import load_incidence_data_sources


def parse_arguments():
    parser = argparse.ArgumentParser(description="Calculate CRHF values for a specific gene.")
    parser.add_argument("--dataset", required=True, help="Specify the dataset (e.g., ci5_ix)")
    parser.add_argument("--population", help="Specify the population by key number (e.g., 38402499)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "SILENT"],
                        help="Set the logging level")
    parser.add_argument("--force-download", action="store_true", help="Force data re-download")
    parser.add_argument("--phenotypes", nargs='+', required=True,
                        help="Specify phenotypes to include (e.g., BreastCancer OvarianCancer).")
    parser.add_argument("--gene", required=True, help="Specify the gene for CRHF calculation (e.g., BRCA1)")
    parser.add_argument("--crhftype", default="constant", help="Specify the CRHF model type to use (default: constant)")
    args = parser.parse_args()
    args.phenotypes = list(set(args.phenotypes))  # Remove duplicates
    return args
    
def main():
    args = parse_arguments()
    setup_logging(args.log_level)
    
    # Load dataset configuration
    sources = load_incidence_data_sources()["sources"]
    if args.dataset not in sources:
        logging.error(f"Dataset '{args.dataset}' not found in sources.yaml.")
        return

    source_config = sources[args.dataset]
    data_handler = DataSourceHandlerFactory.create_data_source_handler(source_config, force_download=args.force_download)
    data_handler.handle_data()

    # Load and process incidence data
    data_parser = IncidenceDataModelFactory.create_incidence_model(source_config, population=args.population)
    df = data_parser.parse_data()
    df = data_parser.filter_by_phenotypes(df, args.phenotypes)
    df = data_parser.build_incidence_table(df)
    df = data_parser.add_age_span_column(df)
    df = data_parser.add_incidence_rate_column()
    logging.info(f"Data for {args.dataset} and population {data_parser.population} processed successfully.")

    # Initialize CRHF model
    crhf_model = CRHFModelFactory.create_model(args.crhftype, args.gene, df)

    # Define an empty list to store CRHF results
    crhf_results = []

    # Calculate CRHF values for each gender and age class
    for gender in df['gender'].unique():
        for age_upper in sorted(df['age_class_upper'].unique()):
            if pd.isna(age_upper):
                logging.info(f"Skipping age classes with undefined span for CRHF calculation.")
                continue
            age_row = df[(df['age_class_upper'] == age_upper) & (df['gender'] == gender)].iloc[0]
            age_lower = age_row['age_class_lower']
            age_span = age_row['age_span']
            
            # Calculate CRHF for the given parameters
            crhf_value = crhf_model.calculate_crhf(gender, age_upper)

            # Append the results to the list as a dictionary
            crhf_results.append({
                'gene': args.gene,
                'gender': gender,
                'age_class_lower': age_lower,
                'age_class_upper': age_upper,
                'age_span': age_span,
                'crhf_value': crhf_value
            })

    # Convert results to a DataFrame and output
    crhf_df = pd.DataFrame(crhf_results)
    print(crhf_df)

if __name__ == "__main__":
    main()
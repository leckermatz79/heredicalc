# bin/relative_risks.py
import logging
import argparse
import pandas as pd
from heredicalc.core.setup_logging import setup_logging
from heredicalc.core.setup_data_sources import load_incidence_data_sources
from heredicalc.incidences.incidence_data_source_handlers.data_source_handler_factory import DataSourceHandlerFactory
from heredicalc.incidences.incidence_models.incidence_data_model_factory import IncidenceDataModelFactory
from heredicalc.penetrances.relative_risk_models.relative_risk_model_factory import RelativeRiskModelFactory

def parse_arguments():
    parser = argparse.ArgumentParser(description="Calculate relative risks for specified phenotypes.")
    parser.add_argument("--dataset", required=True, help="Specify the dataset (e.g., ci5_ix)")
    parser.add_argument("--population", help="Specify the population by key number (e.g., 38402499)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "SILENT"],
                        help="Set the logging level")
    parser.add_argument("--force-download", action="store_true", help="Force data re-download")
    parser.add_argument("--phenotypes", nargs='+', required=True,
                        help="Specify phenotypes to include (e.g., BreastCancer OvarianCancer).")
    parser.add_argument("--rr_model", default="static_lookup", help="Specify the relative risk model to use (default: static_lookup)")
    parser.add_argument("--gene", required=True, help="Specify the gene of interest for relative risk calculation (e.g., BRCA1)")
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

    # Load and process data
    data_parser = IncidenceDataModelFactory.create_incidence_model(source_config, population=args.population)
    df = data_parser.parse_data()
    df = data_parser.filter_by_phenotypes(df, args.phenotypes)
    df = data_parser.build_incidence_table(df)
    logging.info(f"Data for {args.dataset} and population {data_parser.population} processed successfully.")

    # Initialize relative risk model
    rr_model = RelativeRiskModelFactory.create_model(args.rr_model, gene=args.gene, data_frame=df)

    # Calculate relative risks for each phenotype, gender, and age class
    rr_results = []
    for gender in df['gender'].unique():
        for phenotype in args.phenotypes:
            for age_upper in sorted(df['age_class_upper'].unique()):
                if pd.isna(age_upper):
                    logging.info(f"Skipping undefined age class for RR calculation.")
                    continue

                # Calculate RR values
                rr_het, rr_hom = rr_model.calculate_relative_risk(age=age_upper, phenotype=phenotype, gender=gender)

                # Store result as dictionary
                rr_results.append({
                    'gender': gender,
                    'phenotype': phenotype,
                    'age_class_upper': age_upper,
                    'rr_het': rr_het,
                    'rr_hom': rr_hom
                })

    # Convert results to a DataFrame and display
    rr_df = pd.DataFrame(rr_results)
    print(rr_df)

if __name__ == "__main__":
    main()
bin/cumulative_risks.py
import logging
import argparse
import pandas as pd
from src.core.setup_logging import setup_logging
from src.core.setup_data_sources import load_incidence_data_sources
from src.incidences.incidence_data_source_handlers.data_source_handler_factory import DataSourceHandlerFactory
from src.incidences.incidence_models.incidence_data_model_factory import IncidenceDataModelFactory
from src.cumulative_risks.cumulative_risk_model_factory import CumulativeRiskModelFactory

def parse_arguments():
    parser = argparse.ArgumentParser(description="Calculate cumulative risks for specified phenotypes.")
    parser.add_argument("--dataset", required=True, help="Specify the dataset (e.g., ci5_ix)")
    parser.add_argument("--population", help="Specify the population by key number (e.g., 38402499)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "SILENT"],
                        help="Set the logging level")
    parser.add_argument("--force-download", action="store_true", help="Force data re-download")
    parser.add_argument("--phenotypes", nargs='+', required=True,
                        help="Specify phenotypes to include (e.g., BreastCancer OvarianCancer).")
    parser.add_argument("--crtype", default="simple", help="Specify the cumulative risk model to use (default: simple)")
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
    df = data_parser.add_age_span_column(df)
    df = data_parser.add_incidence_rate_column()
    logging.info(f"Data for {args.dataset} and population {data_parser.population} processed successfully.")

    # Initialize cumulative risk model
    cumulative_risk_model = CumulativeRiskModelFactory.create_model(args.crtype, df)

    # Define an empty list to store results
    cumulative_risks = []

    # Loop through genders and unique age classes to calculate cumulative risks
    for gender in df['gender'].unique():
        #print ("gender: ", gender)
        for age_upper in sorted(df['age_class_upper'].unique()):
            #print ("age_upper: ", age_upper)
            if pd.isna(age_upper):
                logging.info(f"Skipping age classes with undefined span for CR calculation.")
                continue
            age_row = df[(df['age_class_upper'] == age_upper) & (df['gender'] == gender)].iloc[0]
            age_lower = age_row['age_class_lower']
            age_span = age_row['age_span']
            cumulative_risk = cumulative_risk_model.calculate_cumulative_risk(
                gender=gender,
                age_class_upper=age_upper,
                phenotypes=args.phenotypes
            )
            # Append the results to the list as a dictionary
            cumulative_risks.append({
                'gender': gender,
                'age_class_lower': age_lower,
                'age_class_upper': age_upper,
                'age_span': age_span,
                'cumulative_risk': cumulative_risk
            })

    # Convert results to a DataFrame
    cumulative_risk_df = pd.DataFrame(cumulative_risks)
    print(cumulative_risk_df)

if __name__ == "__main__":
    main()
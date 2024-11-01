# V3/bin/penetrances.py
import argparse
import logging
import os
import pandas as pd
import yaml
from V3.core.setup_logging import setup_logging
from V3.incidences.incidence_data_source_handlers.data_source_handler_factory import DataSourceHandlerFactory
from V3.incidences.incidence_models.incidence_data_model_factory import IncidenceDataModelFactory
from V3.cumulative_risk_models.cumulative_risk_model_factory import CumulativeRiskModelFactory
from V3.penetrances.crhf_models.crhf_model_factory import CRHFModelFactory
from V3.penetrances.relative_risk_models.relative_risk_model_factory import RelativeRiskModelFactory
from V3.penetrances.penetrance_models.penetrance_model_factory import PenetranceModelFactory

def parse_arguments():
    parser = argparse.ArgumentParser(description="Calculate penetrance based on specified models and parameters.")
    parser.add_argument("--dataset", required=True, help="Specify the dataset (e.g., ci5_ix)")
    parser.add_argument("--population", help="Specify the population by key number (optional)")
    parser.add_argument("--phenotypes", nargs='+', required=True, help="List of phenotypes to analyze (e.g., BreastCancer OvarianCancer)")
    parser.add_argument("--gene", required=True, help="Specify the gene (e.g., BRCA1)")
    parser.add_argument("--crhf_model_type", default="constant", help="Choose CRHF model type (default: constant)")
    parser.add_argument("--rr_model_type", default="static_lookup", help="Choose relative risk model type (default: static_lookup)")
    parser.add_argument("--cr_model_type", default="simple", help="Choose cumulative risk model type (default: simple)")
    parser.add_argument("--penetrance_model_type", default="uniform", help="Choose penetrance model type (default: uniform)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "SILENT"], help="Set the logging level")
    parser.add_argument("--force-download", action="store_true", help="Force data re-download if needed")
    args = parser.parse_args()
    args.phenotypes = list(set(args.phenotypes))  # Remove duplicates in phenotype list
    return args

def load_sources():
    sources_path = os.path.join(os.path.dirname(__file__), ".." , "data_sources", "incidences", "sources.yaml")
    with open(sources_path, "r") as f:
        return yaml.safe_load(f)

def main():
    args = parse_arguments()
    setup_logging(args.log_level)
    
    # Load and validate the dataset configuration
    sources = load_sources()["sources"]
    if args.dataset not in sources:
        logging.error(f"Dataset '{args.dataset}' not found in sources.yaml.")
        return

    source_config = sources[args.dataset]
    data_handler = DataSourceHandlerFactory.create_data_source_handler(source_config, force_download=args.force_download)
    data_handler.handle_data()

    # Load incidence data and process it
    data_parser = IncidenceDataModelFactory.create_incidence_model(source_config, population=args.population)
    df = data_parser.parse_data()
    df = data_parser.filter_by_phenotypes(df, args.phenotypes)
    df = data_parser.build_incidence_table(df)
    df = data_parser.add_age_span_column(df)
    df = data_parser.add_incidence_rate_column()

    # Initialize model instances
    crhf_model = CRHFModelFactory.create_model(args.crhf_model_type, args.gene, df)
    rr_model = RelativeRiskModelFactory.create_model(args.rr_model_type, args.gene, df)
    cr_model = CumulativeRiskModelFactory.create_model(args.cr_model_type, df)
    penetrance_model = PenetranceModelFactory.create_model(args.penetrance_model_type, args.gene, df, crhf_model, rr_model, cr_model)

    # Define an empty list to store results
    penetrance_data = []
    liability_class_id = 1  # Initialize liability class ID counter

    # Loop through phenotypes, genders, and unique age classes to calculate penetrance
    for phenotype in args.phenotypes:
        for gender in df['gender'].unique():
            for age_upper in sorted(df['age_class_upper'].unique()):
                if pd.isna(age_upper):
                    continue

                age_row = df[(df['age_class_upper'] == age_upper) & (df['gender'] == gender)].iloc[0]
                age_lower = age_row['age_class_lower']

                # Calculate cumulative risk, CRHF, and relative risks
                cumulative_risk = cr_model.calculate_cumulative_risk(gender, age_upper, [phenotype])
                crhf_value = crhf_model.calculate_crhf(gender, age_upper)
                rr_het, rr_hom = rr_model.calculate_relative_risk(age_upper, phenotype, gender)

                # Calculate penetrance values
                penetrance_nc, penetrance_het, penetrance_hom = penetrance_model.calculate_penetrance(
                    cumulative_risk, crhf_value, rr_het, rr_hom
                )

                # Append the results to the list as a dictionary
                penetrance_data.append({
                    'liability_class_id': liability_class_id,
                    'penetrance_nc': penetrance_nc,
                    'penetrance_het': penetrance_het,
                    'penetrance_hom': penetrance_hom,
                    'phenotype': phenotype,
                    'gender': gender,
                    'age_upper': age_upper,
                    'age_lower': age_lower
                })
                liability_class_id += 1  # Increment ID for next liability class

    # Convert results to a DataFrame and display it
    penetrance_df = pd.DataFrame(penetrance_data)
    print(penetrance_df)

if __name__ == "__main__":
    main()
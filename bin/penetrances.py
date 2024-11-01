# V3/bin/penetrances.py
import argparse
import os
import logging
import pandas as pd
from V3.core.setup_logging import setup_logging
from V3.incidences.incidence_data_source_handlers.data_source_handler_factory import DataSourceHandlerFactory
from V3.incidences.incidence_models.incidence_data_model_factory import IncidenceDataModelFactory
from V3.cumulative_risk_models.cumulative_risk_model_factory import CumulativeRiskModelFactory
from V3.penetrances.crhf_models.crhf_model_factory import CRHFModelFactory
from V3.penetrances.relative_risk_models.relative_risk_model_factory import RelativeRiskModelFactory
from V3.penetrances.penetrance_models.penetrance_model_factory import PenetranceModelFactory

def parse_arguments():
    parser = argparse.ArgumentParser(description="Calculate penetrances for specified phenotypes.")
    parser.add_argument("--dataset", required=True, help="Specify the dataset (e.g., ci5_ix)")
    parser.add_argument("--population", help="Specify the population by key number (e.g., 38402499)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "SILENT"],
                        help="Set the logging level")
    parser.add_argument("--force-download", action="store_true", help="Force data re-download")
    parser.add_argument("--phenotypes", nargs='+', required=True,
                        help="Specify phenotypes to include (e.g., BreastCancer OvarianCancer).")
    parser.add_argument("--crhftype", default="constant", help="Specify the CRHF model type to use")
    parser.add_argument("--rrtype", default="static_lookup", help="Specify the relative risk model type to use")
    parser.add_argument("--penetrancetype", default="uniform_survival", help="Specify the penetrance model type to use")
    parser.add_argument("--gene", required=True, help="Specify the gene for which penetrance is calculated")
    return parser.parse_args()

def load_sources():
    """Loads the sources.yaml file and returns its contents."""
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

    # Load and process data
    data_parser = IncidenceDataModelFactory.create_incidence_model(source_config, population=args.population)
    df = data_parser.parse_data()
    df = data_parser.filter_by_phenotypes(df, args.phenotypes)
    df = data_parser.build_incidence_table(df)
    df = data_parser.add_age_span_column(df)
    df = data_parser.add_incidence_rate_column()
    logging.info(f"Data for {args.dataset} and population {data_parser.population} processed successfully.")

    # Initialize cumulative risk, CRHF, and relative risk models
    cumulative_risk_model = CumulativeRiskModelFactory.create_model("simple", df)
    crhf_model = CRHFModelFactory.create_model(args.crhftype, gene=args.gene, data_frame=df)
    relative_risk_model = RelativeRiskModelFactory.create_model(args.rrtype, gene=args.gene, df=df)
    penetrance_model = PenetranceModelFactory.create_penetrance_model(args.penetrancetype, df, relative_risk_model, crhf_model)
    
    # Define an empty list to store results
    penetrance_data = []

    # Loop through each gender, age class, and phenotype combination
    for gender in df['gender'].unique():
        for age_upper in sorted(df['age_class_upper'].unique()):
            if pd.isna(age_upper):
                logging.info("Skipping undefined age spans.")
                continue
            
            age_row = df[(df['age_class_upper'] == age_upper) & (df['gender'] == gender)].iloc[0]
            age_lower = age_row['age_class_lower']
            age_span = age_row['age_span']
            incidence_rate = age_row['incidence_rate']

            for phenotype in args.phenotypes + ["Unaffected"]:
                cumulative_risk = cumulative_risk_model.calculate_cumulative_risk(gender=gender, age_class_upper=age_upper, phenotypes=args.phenotypes)
                crhf = crhf_model.calculate_crhf(gender=gender, age_class_upper=age_upper)
                rr_het, rr_hom = relative_risk_model.calculate_relative_risk(age_upper, phenotype, gender)

                # Calculate penetrance
                penetrance_nc, penetrance_het, penetrance_hom = penetrance_model.calculate_penetrance(
                    gene=args.gene, phenotype=phenotype, cumulative_risk=cumulative_risk, 
                    incidence_rate=incidence_rate, crhf=crhf, rr_het=rr_het, rr_hom=rr_hom, 
                    gender=gender, age_class_upper=age_upper
                )

                # Append result
                penetrance_data.append({
                    'liability_class_id': f"{args.gene}_{gender}_{age_upper}",
                    'penetrance_nc': penetrance_nc,
                    'penetrance_het': penetrance_het,
                    'penetrance_hom': penetrance_hom,
                    'phenotype': phenotype,
                    'gender': gender,
                    'age_class_lower': age_lower,
                    'age_class_upper': age_upper
                })
    
    # Convert results to a DataFrame and output
    penetrance_df = pd.DataFrame(penetrance_data)
    print(penetrance_df)

if __name__ == "__main__":
    main()
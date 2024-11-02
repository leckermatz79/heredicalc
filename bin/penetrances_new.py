# V3/bin/penetrances_new.py
import argparse
import os
import logging
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
    parser = argparse.ArgumentParser(description="Calculate penetrance data with specified parameters.")
    parser.add_argument("--dataset", required=True, help="Specify the dataset (e.g., ci5_ix)")
    parser.add_argument("--population", help="Specify the population by key number (e.g., 38402499)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "SILENT"],
                        help="Set the logging level")
    parser.add_argument("--force-download", action="store_true", help="Force data re-download")
    parser.add_argument("--phenotypes", nargs='+', required=True,
                        help="Specify phenotypes to include (e.g., BreastCancer OvarianCancer).")
    parser.add_argument("--crhf_model", default="constant", help="Specify the CRHF model (default: constant)")
    parser.add_argument("--rr_model", default="static_lookup", help="Specify the RR model (default: static_lookup)")
    parser.add_argument("--penetrance_model", default="uniform_survival", help="Specify the penetrance model")
    parser.add_argument("--cr_model", default="simple", help="Specify the cumulative risk model (default: simple)")
    parser.add_argument("--gene", required=True, help="Specify the gene for CRHF calculation")
    return parser.parse_args()

def load_sources():
    sources_path = os.path.join(os.path.dirname(__file__), "../data_sources/incidences/sources.yaml")
    with open(sources_path, "r") as f:
        return yaml.safe_load(f)

def main():
    args = parse_arguments()
    setup_logging(args.log_level)
    pd.options.display.float_format = '{:.10e}'.format

    sources = load_sources()["sources"]
    if args.dataset not in sources:
        logging.error(f"Dataset '{args.dataset}' not found in sources.yaml.")
        return

    source_config = sources[args.dataset]
    data_handler = DataSourceHandlerFactory.create_data_source_handler(source_config, force_download=args.force_download)
    data_handler.handle_data()

    data_parser = IncidenceDataModelFactory.create_incidence_model(source_config, population=args.population)
    df = data_parser.parse_data()
    df = data_parser.filter_by_phenotypes(df, args.phenotypes)
    df = data_parser.build_incidence_table(df)
    df = data_parser.add_age_span_column(df)
    df = data_parser.add_incidence_rate_column()
    logging.info(f"Data for {args.dataset} and population {data_parser.population} processed successfully.")

    crhf_model = CRHFModelFactory.create_model(args.crhf_model, args.gene, df)
    rr_model = RelativeRiskModelFactory.create_model(args.rr_model, args.gene, df)

    # Calculate and add CRHF and RR values to central_df
    for idx, row in df.iterrows():
        crhf_value = crhf_model.calculate_crhf(row['gender'], row['age_class_upper'])
        rr_het, rr_hom = rr_model.calculate_relative_risk(
            age=row['age_class_upper'], phenotype=row['phenotype'], gender=row['gender']
        )
        df.at[idx, 'crhf'] = crhf_value
        df.at[idx, 'rr_het'] = rr_het
        df.at[idx, 'rr_hom'] = rr_hom

    # Calculate lambda values for nc, het, hom based on incidence rates, crhf, and rr
    df['lambda_nc'] = df.apply(
        lambda row: row['incidence_rate'] / ((1 - row['crhf']) + row['crhf'] * row['rr_het']) 
        if pd.notnull(row['incidence_rate']) and pd.notnull(row['age_class_upper']) else 0,
        axis=1
    )
    df['lambda_het'] = df.apply(
        lambda row: row['lambda_nc'] * row['rr_het'] if pd.notnull(row['age_class_upper']) else 0,
        axis=1
    )
    df['lambda_hom'] = df.apply(
        lambda row: row['lambda_nc'] * row['rr_hom'] if pd.notnull(row['age_class_upper'] and pd.notnull(row['rr_hom'])) else 0,
        axis=1
    )

    logging.info("Calculated lambda values for nc, het, hom and added to central_df.")
    
    print("Central DataFrame with lambda values:")
    print(df[['gender', 'age_class_upper', 'phenotype', 'incidence_rate', 'lambda_nc', 'lambda_het', 'lambda_hom', 'rr_hom']])

if __name__ == "__main__":
    main()
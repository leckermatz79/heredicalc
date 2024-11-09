# bin/incidences.py
import logging
import argparse
from core.setup_logging import setup_logging
from incidences.incidence_data_source_handlers.data_source_handler_factory import DataSourceHandlerFactory
from incidences.incidence_models.incidence_data_model_factory import IncidenceDataModelFactory
from core.setup_data_sources import load_incidence_data_sources

def parse_arguments():
    parser = argparse.ArgumentParser(description="Incidences data handler.")
    parser.add_argument("--dataset", required=True, help="Specify the dataset (e.g., ci5_ix)")
    parser.add_argument("--population", help="Specify the population by key number (e.g., 38402499)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "SILENT"],
                        help="Set the logging level")
    parser.add_argument("--force-download", action="store_true", help="Force data re-download")
    parser.add_argument("--phenotypes", nargs='+', required=True,
                        help="Specify phenotypes to include (e.g., BreastCancer OvarianCancer).")
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
    logging.info(f"Data for {args.dataset} and population {data_parser.population} processed successfully.")

    # Filter and build incidence table
    df = data_parser.filter_by_phenotypes(df, args.phenotypes)
    incidence_table = data_parser.build_incidence_table(df)
    incidence_table = data_parser.add_incidence_rate_column()
    incidence_table = data_parser.add_age_span_column(incidence_table) 
    #pd.set_option('display.max_rows', None)
    #pd.set_option('display.max_columns', None)
    #df_filtered = incidence_table[
    #    (incidence_table['gender'] == 'F') &
    #    (incidence_table['age_class_lower'] == 30.0) &
    #    (incidence_table['age_class_upper'] == 34.0)
    #]
    #print (df_filtered)
    print(incidence_table)

if __name__ == "__main__":
    main()
# bin/penetrances.py
import argparse
import logging
import pandas as pd
import numpy as np
import sys
from src.core.setup_logging import setup_logging
from src.core.setup_data_sources import load_incidence_data_sources
from src.incidences.incidence_data_source_handlers.data_source_handler_factory import DataSourceHandlerFactory
from src.incidences.incidence_models.incidence_data_model_factory import IncidenceDataModelFactory
from src.cumulative_risks.cumulative_risk_model_factory import CumulativeRiskModelFactory
from src.penetrances.crhf_models.crhf_model_factory import CRHFModelFactory
from src.penetrances.relative_risk_models.relative_risk_model_factory import RelativeRiskModelFactory
from src.penetrances.penetrance_models.penetrance_model_factory import PenetranceModelFactory
from src.penetrances.exporters.penetrance_exporter_factory import PenetranceExporterFactory

def parse_arguments():
    parser = argparse.ArgumentParser(description="Calculate penetrance for specified parameters.")
    parser.add_argument("--dataset", required=True, help="Specify the dataset (e.g., ci5_ix)")
    parser.add_argument("--population", help="Specify the population by key number (e.g., 38402499)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "SILENT"],
                        help="Set the logging level")
    parser.add_argument("--force_download", type=str, choices=["no", "yes", "ask"], default="no", 
                        help="Force fresh download of incidence data, if applicalbe 'no' (default), 'yes' to force download, or 'ask' to confirm.")
    parser.add_argument("--phenotypes", nargs='+', required=True,
                        help="Specify phenotypes to include (e.g., BreastCancer OvarianCancer).")
    parser.add_argument("--crhf_model", default="constant", help="Specify the CRHF model to use (default: constant)")
    parser.add_argument("--rr_model", default="static_lookup", help="Specify the RR model to use (default: static_lookup)")
    parser.add_argument("--penetrance_model", default="uniform_survival", help="Specify the penetrance model to use (default: uniform_survival)")
    parser.add_argument("--cr_model", default="simple", help="Specify the cumulative risk model to use (default: simple)")
    parser.add_argument("--gene", required=True, help="Specify the gene for CRHF calculation")
    parser.add_argument("--output_format", default="plain", help="Specify the output format. (default: plain)")
    parser.add_argument("--output_file", default="stdout", help="Specify output file. (default: stdout)")
    return parser.parse_args()

def run_penetrance_calculation(dataset, population, log_level="INFO", force_download=False, phenotypes=None,
                               crhf_model="constant", rr_model="static_lookup", penetrance_model="uniform_survival",
                               cr_model="simple", gene=None, output_format="plain", output_file="stdout"):
    # Load dataset configuration
    sources = load_incidence_data_sources()["sources"]
    if dataset not in sources:
        logging.error(f"Dataset '{dataset}' not found in sources.yaml.")
        return

    source_config = sources[dataset]
    data_handler = DataSourceHandlerFactory.create_data_source_handler(source_config, force_download=force_download)
    data_handler.handle_data()

    # Load and process incidence data
    data_parser = IncidenceDataModelFactory.create_incidence_model(source_config, population=population)
    df = data_parser.parse_data()
    df = data_parser.filter_by_phenotypes(df, phenotypes)
    df = data_parser.build_incidence_table(df)
    df = data_parser.add_age_span_column(df)
    df = data_parser.add_incidence_rate_column()
    logging.info(f"Data for {dataset} and population {data_parser.population} processed successfully.")

    # Initialize cumulative risk model
    cr_model = CumulativeRiskModelFactory.create_model(cr_model, df)
        # DataFrame for cumulative risks
    cumulative_risks = []
    for gender in df['gender'].unique():
        #for age_upper in sorted(df['age_class_upper'].unique()):
        for age_lower in sorted(df['age_class_lower'].unique()):
            # Standard handling for defined age classes
            logging.debug(f"gender: {gender}, age_class_lower: {age_lower}")
            if not np.isnan(age_lower):
                age_upper = df[(df['gender'] == gender) & (df['age_class_lower'] == age_lower)]['age_class_upper'].iloc[0]
            else:
                #continue
                age_upper = np.nan
            logging.debug(f"Age Upper: {age_upper}")
            if isinstance(age_upper, (int, float)) and not np.isnan(age_upper):
                logging.debug ("Calculating.")
                cumulative_risk = cr_model.calculate_cumulative_risk(
                    gender=gender,
                    age_class_upper=age_upper,
                    phenotypes=phenotypes
                )
            else:
                cumulative_risk = np.nan
                logging.debug (f"Setting to {cumulative_risk}.")


            # Add the entry to cumulative_risks
            current_risk = {
                'gender': gender,
                'age_class_upper': age_upper,
                'age_class_lower': age_lower,
                'cr_gen': cumulative_risk,
                'cr_nc': np.nan,  # Placeholder for non-carrier CR
                'cr_het': np.nan,  # Placeholder for heterozygote CR
                'cr_hom': np.nan   # Placeholder for homozygote CR
            }
            
            cumulative_risks.append(current_risk)
            logging.info("current risk appended.")

    cumulative_risk_df = pd.DataFrame(cumulative_risks)

    crhf_model = CRHFModelFactory.create_model(crhf_model, gene, df)
    rr_model = RelativeRiskModelFactory.create_model(rr_model, gene, df)

    # Calculate lambda values and add to central_df
    for idx, row in df.iterrows():
        crhf = crhf_model.calculate_crhf(row['gender'], row['age_class_upper'])
        rr_het, rr_hom = rr_model.calculate_relative_risk(
            age=row['age_class_upper'],
            phenotype=row['phenotype'],
            gender=row['gender']
        )
        
        # Calculate lambda values
        lambda_nc = row['incidence_rate'] / ((1 - crhf) + crhf * rr_het)
        lambda_het = lambda_nc * rr_het
        lambda_hom = lambda_nc * rr_hom if not pd.isna(rr_hom) else 0

        # Store lambda values in the central DataFrame
        df.loc[idx, 'lambda_nc'] = lambda_nc
        df.loc[idx, 'lambda_het'] = lambda_het
        df.loc[idx, 'lambda_hom'] = lambda_hom
 
    #print(cumulative_risk_df)

    # Calculate cumulative risks for non-carriers, heterozygotes, and homozygotes
    for idx, row in cumulative_risk_df.iterrows():
        age_upper = row['age_class_upper']
        gender = row['gender']
        
        # Filter central_df to get sum of lambda values up to current age class
        relevant_df = df[(df['gender'] == gender) & (df['age_class_upper'] <= age_upper)]
        
        # Calculate cumulative risk for non-carriers
        lambda_nc_sum = (relevant_df['lambda_nc'] * relevant_df['age_span']).sum()
        cumulative_risk_df.loc[idx, 'cr_nc'] = 1 - np.exp(-lambda_nc_sum)

        # Calculate cumulative risk for heterozygotes
        lambda_het_sum = (relevant_df['lambda_het'] * relevant_df['age_span']).sum()
        cumulative_risk_df.loc[idx, 'cr_het'] = 1 - np.exp(-lambda_het_sum)

        # Calculate cumulative risk for homozygotes
        lambda_hom_sum = (relevant_df['lambda_hom'] * relevant_df['age_span']).sum()
        cumulative_risk_df.loc[idx, 'cr_hom'] = 1 - np.exp(-lambda_hom_sum)

    penetrance_model = PenetranceModelFactory.create_model(penetrance_model, df, cumulative_risk_df)

    # Calculate penetrance for each liability class
    df = penetrance_model.calculate_penetrance(df, cumulative_risk_df)
    # Select required columns for the final liability classes DataFrame
    
    liability_classes_df = df[['gender', 'phenotype', 'age_class_lower', 'age_class_upper', 
                               'penetrance_nc', 'penetrance_het', 'penetrance_hom']]
    
    # Add unaffected rows at the top
    unaffected_rows = cumulative_risk_df[['gender', 'age_class_upper', 'age_class_lower', 'cr_nc', 'cr_het', 'cr_hom']].copy()
    unaffected_rows['phenotype'] = 'Unaffected'
    unaffected_rows.rename(columns={'cr_nc': 'penetrance_nc', 'cr_het': 'penetrance_het', 'cr_hom': 'penetrance_hom'}, inplace=True)
    liability_classes_df = pd.concat([unaffected_rows, liability_classes_df], ignore_index=True)

    # Sort and reset index with new label 'liability_class'
    #liability_classes_df.sort_values(by=['gender', 'age_class_upper'], inplace=True)
    liability_classes_df.reset_index(drop=True, inplace=True)
    liability_classes_df.index.name = 'liability_class'
    liability_classes_df = liability_classes_df[['gender', 'phenotype', 'age_class_lower', 'age_class_upper', 'penetrance_nc', 'penetrance_het', 'penetrance_hom']]

    # Output final liability class penetrance data
    #print (liability_classes_df)

    # Create the exporter and export data
    logging.debug(f"Exporting data in {output_format} format to {output_file}.")
    exporter = PenetranceExporterFactory.create_exporter(output_format, output_file)
    result = exporter.export_data(liability_classes_df)
    logging.debug("Export completed.")
    return result 

def main():
    args = parse_arguments()
    result = run_penetrance_calculation(
        dataset=args.dataset,
        population=args.population,
        log_level=args.log_level,
        force_download=args.force_download,
        phenotypes=args.phenotypes,
        crhf_model=args.crhf_model,
        rr_model=args.rr_model,
        penetrance_model=args.penetrance_model,
        cr_model=args.cr_model,
        gene=args.gene,
        output_format=args.output_format,
        output_file=args.output_file
    )

if __name__ == "__main__":
    main()
import argparse
import subprocess
import tempfile
import logging
from pathlib import Path
from src.pedconv.pedconv.pedigree import Pedigree
from src.pedconv.exporters.pedigree_exporter_factory import PedigreeExporterFactory
from src.pedconv.importers.pedigree_importer_factory import PedigreeImporterFactory
from src.penetrances.exporters.penetrance_exporter_factory import PenetranceExporterFactory
from src.flb.liabilities_mapper import map_liabilities
#from pedconv.exporters import FLBExporter
from hashlib import md5
import sys
import pandas as pd
from src.core.config import PROJECT_ROOT

CACHE_DIR = Path("cache")  # Directory for cached liabilities
CLI_CUTOFF = 10*1024

def validate_args(args):
    # Validate the arguments provided by the user

    # If both liabilities_file and recalculation parameters are provided
    if args.liabilities_file and (args.dataset or args.population or args.phenotypes or args.gene or args.crhf_model or args.rr_model or args.cr_model or args.penetrance_model):
        logging.error("Error: You specified both a liabilities file and parameters for recalculating liabilities.")
        logging.error("Please provide either a liabilities file or the parameters for recalculation, not both.")
        logging.error("Use flb.py --help for more information.")
        sys.exit(1)

    # If no liabilities_file is provided, ensure all recalculation parameters are present
    if not args.liabilities_file and not (args.dataset and args.population and args.phenotypes and args.gene and args.crhf_model and args.rr_model and args.cr_model and args.penetrance_model):
        logging.error("Error: No liabilities file specified, and missing parameters for recalculation.")
        logging.error("Please specify either a liabilities file or provide all required parameters for recalculation.")
        logging.error("Use flb.py --help for more information.")
        sys.exit(1)

    # Validate force_recalculate to be one of the allowed options
    if args.force_recalculate not in ["no", "yes", "ask"]:
        logging.error("Error: --force-recalculate must be one of 'no', 'yes', or 'ask'.")
        logging.error("Use flb.py --help for more information.")
        sys.exit(1)

def generate_hash(dataset, population, phenotypes, gene, crhf_model, rr_model, cr_model, penetrance_model):
    # Generate an md5 hash from the input parameters to create a unique cache identifier
    data_string = f"{dataset}_{population}_{'_'.join(sorted(phenotypes))}_{gene}_{crhf_model}_{rr_model}_{cr_model}_{penetrance_model}"
    return md5(data_string.encode()).hexdigest()

def check_cache(hash_value):
    # Check if a cached file for the hash value exists
    cache_file = CACHE_DIR / f"{hash_value}_liabilities.pkl"
    return cache_file if cache_file.exists() else None

def calculate_liabilities(dataset, population, phenotypes, gene, crhf_model, rr_model, cr_model, hash_value, penetrance_model):
    # Run penetrances.py to recalculate liabilities and save to cache
    cache_file = CACHE_DIR / f"{hash_value}_liabilities.pkl"
    result = subprocess.run(
        ["python", "src/bin/penetrances.py", "--dataset", dataset,
         "--population", population, "--phenotypes", *phenotypes, "--gene", gene,
         "--crhf_model", crhf_model, "--rr_model", rr_model, "--cr_model", cr_model, "--penetrance_model", penetrance_model,
         "--output_format", "plain", "--output_file", str(cache_file)],
        capture_output=False, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error calculating liabilities: {result.stderr}")
    return cache_file

def run_flb_calculation(r_input, use_file=False):
    """
    Runs the FLB calculation in R, using the provided input data.

    Parameters:
    r_input (str or Path): If `use_file` is False, this is a string of R code; otherwise, it's a path to a file.
    use_file (bool): If True, the R input is passed via a file; otherwise, it's passed directly as a string.

    Returns:
    str: The output of the R script (FLB result).
    """
    # Define the R script path
    r_script_path = Path(__file__).resolve().parent.parent / "flb" / "flb_script.R"
    if not r_script_path.exists():
        raise FileNotFoundError(f"R script not found at {r_script_path}")
    
    # Define the arguments for subprocess.run
    if use_file:
        # Pass the file path as an argument to the R script
        result = subprocess.run(
            ["Rscript", r_script_path, r_input],
            capture_output=True, text=True
        )
    else:
        # Pass the R code as stdin to the R script
        result = subprocess.run(
            ["Rscript", r_script_path],
            input=r_input,
            capture_output=True, text=True
        )

    # Check for errors in the R script execution
    if result.returncode != 0:
        raise RuntimeError(f"Error in FLB calculation: {result.stderr}")

    # Return the output of the R script (result from FLB calculation)
    return result.stdout.strip()

def main():
    CACHE_DIR.mkdir(exist_ok=True)

    parser = argparse.ArgumentParser(description="Execute FLB calculation with pedigree and liability data.")
    parser.add_argument("--pedigree_file", type=Path, required=True, help="Path to the pedigree file (e.g., example.ped)")
    parser.add_argument("--pedigree_format", type=str, required=True, help="Format of the pedigree file (e.g., cool)")
    parser.add_argument("--liabilities_file", type=Path, help="Optional path to the liabilities file.")
    parser.add_argument("--dataset", help="Specify the dataset (e.g., ci5_ix)")
    parser.add_argument("--population", help="Specify the population by key number (e.g., 38402499)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set the logging level")
    parser.add_argument("--phenotypes", nargs='+',
                        help="Specify phenotypes to include (e.g., BreastCancer OvarianCancer).")
    parser.add_argument("--crhf_model", help="Specify the CRHF model to use (e.g.: constant)")
    parser.add_argument("--rr_model",  help="Specify the RR model to use (e.g.: static_lookup)")
    parser.add_argument("--penetrance_model",  help="Specify the penetrance model to use (e.g.: uniform_survival)")
    parser.add_argument("--cr_model", help="Specify the cumulative risk model to use (e.g.: simple)")
    parser.add_argument("--gene", help="Specify the gene for CRHF calculation")
    parser.add_argument("--afreq", default="0.0001", help="Specify allele frequency (default: 0.0001)")
    parser.add_argument("--force_recalculate", type=str, choices=["no", "yes", "ask"], default="no", 
                        help="Recalculation option for liabilities: 'no' (default), 'yes' to force recalculation, or 'ask' to confirm.")
    parser.add_argument("--output", type=str, default="stdout", help="Output target: 'stdout' or file path")

    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)
    validate_args(args)


    # Step 1: Load and convert pedigree
    pedigree = Pedigree()
    importer = PedigreeImporterFactory.create_importer(args.pedigree_format, args.pedigree_file)
    importer.import_data(pedigree)
    pedigree.members_df = pedigree.members_df.sort_values(by="id").reset_index(drop=True)
    # print (pedigree.members_df)
    # sys.exit(0)
    exporter = PedigreeExporterFactory.create_exporter("segregatr_flb", None) 
    flb_pedigree = exporter.export_data(pedigree.members_df)  # R-compatible Snippet for FLB
    # pedigree now holds working copy of pedigree, 
    # flb_pedigree now holds pedtools compatible R-snippet for generating "x"-vector and associated affection status and genotype status vectors.

    # Step 2: Prepare liabilities (check cache or recalculate)
    hash_value = generate_hash(args.dataset, args.population, args.phenotypes, args.gene, args.crhf_model, args.rr_model, args.cr_model, args.penetrance_model)
    cached_file = check_cache(hash_value)
    liabilities_data = None
    if cached_file and args.force_recalculate == "ask":
        # Ask user if recalculation is desired
        while True:
            response = input("Cached liabilities data found. Recalculate? (y/n): ").strip().lower()
            if response == 'y':
                args.force_recalculate = "yes"
                break
            elif response =='n':
                args.force_recalculate = "no"
                break
    if cached_file and args.force_recalculate == "no":
        liabilities_file = cached_file
        logging.info(f"Using cached liabilities data: {liabilities_file}")        

    else: 
        # either no cached file, or cached file and force_recalculate = yes
        # (re)calculate liability, and save to file
        try:
            liabilities_file = calculate_liabilities(
                args.dataset, args.population, args.phenotypes, args.gene, 
                args.crhf_model, args.rr_model, args.cr_model, hash_value, args.penetrance_model
            )
            logging.info(f"(Re-)calculated and cached liabilities data: {liabilities_file}")
        except RuntimeError as e:
            logging.error(f"Failed to calculate liabilities: {e}")
            sys.exit(1)

    liabilities_data = pd.read_pickle(liabilities_file) 
    if liabilities_data.empty:
        # this is wrong, and the liability data is missing!
        logging.error ("Loading / calculating liability data failed.")
        sys.exit(1)


    # Step 3: Map liabilities to pedigree
    liability_vector_str = map_liabilities(liabilities_data, pedigree.members_df)
    if not liability_vector_str:
        logging.error("Failed to map liabilities to pedigree.")
        sys.exit(1)

    # Step 4: Export liabilities in FLB format
    liab_exporter = PenetranceExporterFactory.create_exporter('flb', None)
    if liab_exporter is None:
        logging.error("Failed to create Penetrance exporter for FLB format.")
        sys.exit(1)
    flb_liabilities = liab_exporter.export_data(liabilities_data)

    # Step 5: Concatenate strings for R-script
    allele_freq = float(args.afreq)
    r_input_str = f"{flb_pedigree}\n{liability_vector_str}\n{flb_liabilities}\nallele_freq <- {allele_freq}"
    if len(r_input_str) < CLI_CUTOFF:
        flb_result = run_flb_calculation(r_input_str)
    else:
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            tmpfile.write(r_input_str.encode())
            tmpfile_path = tmpfile.name
        try:
            flb_result = run_flb_calculation(tmpfile_path, use_file=True)
        finally:
            pass
            #Path(tmpfile_path).unlink()  # Delete the temporary file

    # Step 6: Output the FLB result
    if args.output == "stdout":
        print(f"FLB Result:\n{flb_result}")
    else:
        with open(args.output, "w") as f:
            f.write(f"FLB Result:\n{flb_result}")

if __name__ == "__main__":
    main()
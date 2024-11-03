import argparse
from pathlib import Path
import sys
import hashlib
import subprocess
import pandas as pd
from src.flb.liabilities_mapper import map_liabilities


CACHE_DIR = Path("cache")  # Directory for cached liabilities

def validate_args(args):
    # Validate the arguments provided by the user

    # If both liabilities_file and recalculation parameters are provided
    if args.liabilities_file and (args.dataset or args.population or args.phenotypes or args.gene or args.crhf_model or args.rr_model or args.cr_model or args.penetrance_model):
        print("Error: You specified both a liabilities file and parameters for recalculating liabilities.")
        print("Please provide either a liabilities file or the parameters for recalculation, not both.")
        print("Use flb.py --help for more information.")
        sys.exit(1)

    # If no liabilities_file is provided, ensure all recalculation parameters are present
    if not args.liabilities_file and not (args.dataset and args.population and args.phenotypes and args.gene and args.crhf_model and args.rr_model and args.cr_model and args.penetrance_model):
        print("Error: No liabilities file specified, and missing parameters for recalculation.")
        print("Please specify either a liabilities file or provide all required parameters for recalculation.")
        print("Use flb.py --help for more information.")
        sys.exit(1)

    # Validate force_recalculate to be one of the allowed options
    if args.force_recalculate not in ["no", "yes", "ask"]:
        print("Error: --force-recalculate must be one of 'no', 'yes', or 'ask'.")
        print("Use flb.py --help for more information.")
        sys.exit(1)

def generate_hash(dataset, population, phenotypes, gene, crhf_model, rr_model, cr_model, penetrance_model):
    # Generate an md5 hash from the input parameters to create a unique cache identifier
    data_string = f"{dataset}_{population}_{phenotypes}_{gene}_{crhf_model}_{rr_model}_{cr_model}_{penetrance_model}"
    return hashlib.md5(data_string.encode()).hexdigest()

def check_cache(hash_value):
    # Check if a cached file for the hash value exists
    cache_file = CACHE_DIR / f"{hash_value}_liabilities.csv"
    return cache_file if cache_file.exists() else None

def recalculate_liabilities(dataset, population, phenotypes, gene, crhf_model, rr_model, cr_model, hash_value, penetrance_model):
    # Run penetrances.py to recalculate liabilities and save to cache
    cache_file = CACHE_DIR / f"{hash_value}_liabilities.csv"
    result = subprocess.run(
        ["python", "src/bin/penetrances.py", "--dataset", dataset,
         "--population", population, "--phenotypes", *phenotypes, "--gene", gene,
         "--crhf_model", crhf_model, "--rr_model", rr_model, "--cr_model", cr_model, "--penetrance_model", penetrance_model,
         "--output_format", "flb", "--output_file", str(cache_file)],
        capture_output=False, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error calculating liabilities: {result.stderr}")
    return cache_file

def main():
    parser = argparse.ArgumentParser(description="Execute FLB calculation with pedigree and liability data.")
    parser.add_argument("--pedigree_file", type=Path, required=True, help="Path to the pedigree file (e.g., example.ped)")
    parser.add_argument("--pedigree_format", type=str, required=True, help="Format of the pedigree file (e.g., cool)")
    parser.add_argument("--liabilities_file", type=Path, help="Optional path to the liabilities file.")
    parser.add_argument("--dataset", help="Specify the dataset (e.g., ci5_ix)")
    parser.add_argument("--population", help="Specify the population by key number (e.g., 38402499)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "SILENT"],
                        help="Set the logging level")
    parser.add_argument("--phenotypes", nargs='+',
                        help="Specify phenotypes to include (e.g., BreastCancer OvarianCancer).")
    parser.add_argument("--crhf_model", help="Specify the CRHF model to use (default: constant)")
    parser.add_argument("--rr_model",  help="Specify the RR model to use (default: static_lookup)")
    parser.add_argument("--penetrance_model",  help="Specify the penetrance model to use (default: uniform_survival)")
    parser.add_argument("--cr_model", help="Specify the cumulative risk model to use (default: simple)")
    parser.add_argument("--gene", help="Specify the gene for CRHF calculation")
    parser.add_argument("--force_recalculate", type=str, choices=["no", "yes", "ask"], default="no", 
                        help="Recalculation option for liabilities: 'no' (default), 'yes' to force recalculation, or 'ask' to confirm.")
    parser.add_argument("--output", type=str, default="stdout", help="Output target: 'stdout' or file path")

    args = parser.parse_args()
    validate_args(args)

    # Create cache directory if it does not exist
    CACHE_DIR.mkdir(exist_ok=True)

    # Determine if liabilities file should be used directly or recalculated
    if args.liabilities_file:
        liabilities_file = args.liabilities_file
    else:
        # Generate a unique hash for the input parameters
        hash_value = generate_hash(args.dataset, args.population, args.phenotypes, args.gene, args.crhf_model, args.rr_model, args.cr_model, args.penetrance_model)
        
        # Check for cached file
        cached_file = check_cache(hash_value)
        
        # If cached file is available and no recalculation is needed
        if cached_file and args.force_recalculate == "no":
            liabilities_file = cached_file
            print(f"Using cached liabilities data: {liabilities_file}")
        elif cached_file and args.force_recalculate == "ask":
            # Ask user if recalculation is desired
            response = input("Cached liabilities data found. Recalculate? (y/n): ").strip().lower()
            if response == 'y':
                liabilities_file = recalculate_liabilities(args.dataset, args.population, args.phenotypes, args.gene, args.crhf_model, args.rr_model, args.cr_model, hash_value, args.penetrance_model)
                print(f"Recalculated and cached liabilities data: {liabilities_file}")
            else:
                liabilities_file = cached_file
                print(f"Using cached liabilities data: {liabilities_file}")
        else:
            # Recalculate and cache liabilities if not cached or forced
            liabilities_file = recalculate_liabilities(args.dataset, args.population, args.phenotypes, args.gene, args.crhf_model, args.rr_model, args.cr_model, hash_value, args.penetrance_model)
            print(f"Recalculated and cached liabilities data: {liabilities_file}")

        liability_vector_str = map_liabilities(liabilities_file, args.pedigree_file)


if __name__ == "__main__":
    main()
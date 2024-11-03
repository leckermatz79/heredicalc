# ped_convert.py

import argparse
import logging
from pedconv.pedigree import Pedigree
from exporters.pedigree_exporter_factory import PedigreeExporterFactory
from importers.pedigree_importer_factory import PedigreeImporterFactory

def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert pedigree data between different formats.")
    parser.add_argument("--in_format", required=True, help="Specify the import format (e.g., 'cool').")
    parser.add_argument("--out_format", required=True, help="Specify the export format (e.g., 'segregatr_flb').")
    parser.add_argument("--infile", required=True, help="Path to the input pedigree file.")
    parser.add_argument("--outfile", required=True, help="Path to the output file.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "SILENT"],
                        help="Set the logging level.")
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    logging.basicConfig(level=args.log_level)
    logging.info("Starting pedigree data conversion.")

    # Load the pedigree data using the specified importer
    pedigree = Pedigree()
    importer = PedigreeImporterFactory.create_importer(args.in_format, args.infile)
    importer.import_data(pedigree)
    logging.info("Data imported successfully.")

    # Export the pedigree data using the specified exporter
    exporter = PedigreeExporterFactory.create_exporter(args.out_format, args.outfile)
    #exporter.file_path = args.output_file  # Set the output file path directly
    exporter.export_data(pedigree)
    logging.info(f"Data exported successfully to {args.outfile}")

if __name__ == "__main__":
    main()
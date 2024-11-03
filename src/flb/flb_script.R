#!/usr/bin/env Rscript

# Load necessary libraries
library(segregatr)

# Parse command line arguments or stdin input
args <- commandArgs(trailingOnly = TRUE)

if (length(args) == 1) {
  # Input is provided via a file
  input_file <- args[1]
  source(input_file)
} else {
  # Input is provided via stdin
  r_code <- file("stdin")
  source(r_code)
  close(r_code)
}

# Execute FLB calculation
# Assuming x, liability, penetrances, and allele_freq are defined in the input

# 'x' is the pedigree object, 'liability' is a vector, 'penetrances' is a matrix, 'allele_freq' is the allele frequency
flb_result <- FLB(x = x, liability = liability, penetrances = penetrances, freq = allele_freq)

# Print the FLB result to stdout
cat(flb_result)
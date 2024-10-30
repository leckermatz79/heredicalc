# V3/install/install_r_packages.R
# List of required packages
required_packages <- c("pedtools", "segregatr")

install_if_missing <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org")
  }
}

sapply(required_packages, install_if_missing)
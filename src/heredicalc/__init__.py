# src/heredicalc/__init__.py

import subprocess
import time

def check_and_install_r_packages():
    """Check if necessary R packages are installed, and install them if not."""
    required_packages = ["segregatr", "pedtools"]

    for i, package in enumerate(required_packages, start=1):
        print(f"Checking R package {i}/{len(required_packages)}: '{package}'")
        try:
            # Run R command to check for the package and install if missing
            result = subprocess.run(
                [
                    "R", "-e",
                    f"if (!requireNamespace('{package}', quietly = TRUE)) {{ "
                    f"cat('Installing {package}...'); "
                    f"install.packages('{package}', repos='https://cloud.r-project.org') }} else {{ "
                    f"cat('{package} is already installed.')}}"
                ],
                check=True,
                capture_output=True,
                text=True
            )
            # Print the output from R to show installation progress
            print(result.stdout)
            # Short delay to simulate progress
            time.sleep(0.5)
        except subprocess.CalledProcessError as e:
            print(f"Error installing R package '{package}': {e.stderr}")
            raise

    print("All required R packages are checked and installed.")

# Ensure R dependencies are checked and installed on package import
check_and_install_r_packages()
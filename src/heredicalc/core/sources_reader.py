# src/heredicalc/core/sources_reader.py
"""
src/heredicalc/core/sources_reader.py

Provides an interface for reading and querying information from sources.yaml.
"""
import logging
import yaml
from pathlib import Path
from .config import PROJECT_ROOT


class SourcesReader:
    def __init__(self, yaml_path=None):
        self.yaml_path = yaml_path or PROJECT_ROOT / "data_sources" / "incidences" / "sources.yaml"
        self.sources = self._load_sources()

    def _load_sources(self):
        """Load sources from the specified YAML file."""
        try:
            with open(self.yaml_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find {self.yaml_path}")
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error parsing YAML: {e}")
    
    def get_available_datasets(self):
        """Retrieve all available dataset names."""
        return list(self.sources.get("sources", {}).keys())
    
    def get_dataset_info(self, dataset_name):
        """
        Get information for a specific dataset.
        
        Parameters:
            dataset_name (str): The name of the dataset.
        
        Returns:
            dict: Dictionary containing dataset information.
        """
        dataset_info = self.sources.get("sources", {}).get(dataset_name, {})

        # Beschreibung, Kohorte und Populationen extrahieren
        description = dataset_info.get("description", "No description available")
        cohort = dataset_info.get("cohort", "")
        population_mappings = dataset_info.get("population_mappings", {})
        
        # Phänotypen aus den Schlüsseln von phenotype_mappings extrahieren
        phenotype_mappings = dataset_info.get("phenotype_mappings", {})
        phenotypes = list(phenotype_mappings.keys())
        

        # Das finale Dictionary zusammenstellen
        return {
            "description": description,
            "cohort": cohort,
            "population_mappings": population_mappings,
            "phenotypes": phenotypes,  # Verwende die Schlüssel von phenotype_mappings
        }

    def list_available_datasets(self):
        """List all available datasets in sources.yaml."""
        return list(self.sources.get("sources", {}).keys())

    def get_phenotypes_for_dataset(self, dataset_name):
        """Return available phenotypes for a dataset."""
        dataset_info = self.get_dataset_info(dataset_name)
        return dataset_info.get("phenotype_mappings", {}).keys()

    def is_dataset_available_locally(self, dataset_name):
        """Check if the dataset has been downloaded locally."""
        dataset_info = self.get_dataset_info(dataset_name)
        data_dir = dataset_info.get("data_dir")
        return Path(data_dir).exists() if data_dir else False

# Example usage (outside this module):
# reader = SourcesReader()
# available_datasets = reader.list_available_datasets()
# phenotypes = reader.get_phonotypes_for_dataset("ci5_ix")
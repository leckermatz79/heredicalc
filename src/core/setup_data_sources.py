import yaml
import os
from .config import PROJECT_ROOT

def load_incidence_data_sources():
    """Loads the sources.yaml file and returns its contents."""
    sources_path = os.path.join(PROJECT_ROOT, "data_sources", "incidences", "sources.yaml")
    with open(sources_path, "r") as f:
        return yaml.safe_load(f)
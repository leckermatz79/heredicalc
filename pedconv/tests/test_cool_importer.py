import pandas as pd
import os
from exporters.cool_pedigree_exporter import CoolPedigreeExporter
from exporters.segregatr_flb_pedigree_exporter import SegregatrFLBPedigreeExporter
from pedconv.pedigree import Pedigree
from importers.cool_pedigree_importer import CoolPedigreeImporter

# Pfad zur hochgeladenen Datei
file_path = os.path.join(os.path.dirname(__file__), '91-00005-05.ped')

# Instanziere Pedigree und CoolPedigreeImporter
pedigree = Pedigree()
importer = CoolPedigreeImporter(file_path)

# Importiere die Daten
importer.import_data(pedigree)

# Zeige die Mitglieder-Datenstruktur an
print(pedigree.members_df)
exporter = SegregatrFLBPedigreeExporter("./test_segregatExport.R")
#exporter = CoolPedigreeExporter("./test_output.ped")
exporter.export_data(pedigree)
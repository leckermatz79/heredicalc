rr_test.py
import logging
from src.penetrances.relative_risk.static_lookup_rr_model import StaticLookupRRModel

# Set up logging to display debug information in the console
logging.basicConfig(level=logging.DEBUG)

def test_rr_model():
    # Instantiate the StaticLookupRRModel with the "BRCA1" gene
    rr_model = StaticLookupRRModel("BRCA1")

    # Define a set of test cases with (age, phenotype, gender)
    test_cases = [
        (35, "BreastCancer", "F"),
        (55, "BreastCancer", "F"),
        (65, "BreastCancer", "F"),
        (85, "BreastCancer", "F"),
        (45, "OvarianCancer", "F"),
        (30, "OvarianCancer", "F"),
        (50, "PancreaticCancer", "M"),
        (30, "PancreaticCancer", "M"),
        (80, "BreastCancer", "M"),  # Special case for males
        (20, "BreastCancer", "F")  # Outside standard age, testing younger age
    ]

    print("Testing StaticLookupRRModel with various inputs:")
    for age, phenotype, gender in test_cases:
        try:
            heterozygous_rr, homozygous_rr = rr_model.get_relative_risk(age, phenotype, gender)
            #print(f"Relative Risk for {phenotype} at age {age} (Gender: {gender}):")
            #print(f"Heterozygous RR: {heterozygous_rr}, Homozygous RR: {homozygous_rr}")
        except ValueError as e:
            print(f"Error for {phenotype} at age {age} (Gender: {gender}): {e}")

if __name__ == "__main__":
    test_rr_model()
# V3/setup.py
from setuptools import setup, find_packages

setup(
    name="V3",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'incidences=V3.bin.incidences:main', # incidences data handler
            'cumulative_risks=V3.bin.cumulative_risks:main', # cumulative risks data handler
            'relative_risks=V3.bin.relative_risks:main', # cumulative risks data handler
            'crhf=V3.bin.crhf:main', # cumulative risks data handler
            'penetrances=V3.bin.penetrances:main'  # main program
        ],
    },
)
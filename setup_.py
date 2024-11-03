# V3/setup.py
from setuptools import setup, find_packages

setup(
    name="V3",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            'incidences=bin.incidences:main', # incidences data handler
            'cumulative_risks=bin.cumulative_risks:main', # cumulative risks data handler
            'relative_risks=bin.relative_risks:main', # cumulative risks data handler
            'crhf=bin.crhf:main', # cumulative risks data handler
            'penetrances=bin.penetrances:main',  # main program
            'pedconv=bin.ped_convert:main'
        ],
    },
    install_requires=[
        "pandas",
        "numpy",
    ],
)
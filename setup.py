# V3/setup.py
from setuptools import setup, find_packages

setup(
    name="V3",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'penetrances=V3.penetrances.data_handler:main', # penetrances data handler
            'incidences=V3.bin.incidences:main', # incidences data handler
            'main-script=V3.main:main',  # main program
        ],
    },
)
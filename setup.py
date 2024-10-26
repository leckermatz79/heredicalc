# V3/setup.py
from setuptools import setup, find_packages

setup(
    name="V3",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'data-handler=V3.incidences.data_handler:main',  # incidences data handler
            'main-script=V3.main:main',  # main program
        ],
    },
)
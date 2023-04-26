"""Setup file for ew_dta_open_science."""
import os

from setuptools import find_packages
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='ew_dta_science_case_demo',
    description='For creating an demoing the open science case on the ESA HPC.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Earthwave Ltd',
    author_email='info@earthwave.co.uk',
    url='https://github.com/earthwave/ew_dta_science_case_demo',
    python_requires=">=3.9",
    packages=find_packages(),
    # note requirements listed ininstall_requires should be the *minimum required*
    # in order to allow pip to resolve multiple installed packages properly.
    # requirements.txt should contain a specific known working version instead.
    install_requires=[
        'imagecodecs',
        'ipykernel',
        'jupyterlab-git',
        'numpy>1.15',
        'matplotlib',
        'tifffile'
    ],
)
from setuptools import setup, find_packages
from __version__ import __version__

def read_requirements(filename):
    """Read requirements from a file"""
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]

setup(
    name='property_project',
    version=__version__,  # Use the version imported from scripts.__version__
    packages=find_packages(where='scripts'),
    package_dir={'': 'scripts'},
    entry_points={
        'console_scripts': [
            'build=scripts.build:main',  # Adjust if main() is defined in build.py
            'search=scripts.search:main',  # Adjust if main() is defined in search.py
        ],
    },
    install_requires=['pandas', 'tabulate', 'requests', 'pyarrow', 'maskpass', 'fpdf2'],

    author='Josh Mock',
    description='This project builds a database for searching the CCOD and OCOD datasets released by the UK Land Registry (https://use-land-property-data.service.gov.uk/).',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jwmock88/property-database/',
    license=open('LICENSE.md').read()
)

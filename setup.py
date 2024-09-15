from setuptools import setup
from scripts.__version__ import __version__

def read_requirements(filename):
    """Read requirements from a file"""
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]

setup(
    name='property_project',
    version='0.1',
    packages=find_packages(where='scripts'),
    package_dir={'': 'scripts'},
    entry_points={
        'console_scripts': [
            'build=build:main',  # 'build' command to run build.py
            'search=search:main',  # 'search' command to run search.py
        ],
    },
    install_requires=read_requirements('requirements.txt'),  # Read requirements from the file

    author='Josh Mock',
    description='This project builds a database for searching the CCOD and OCOD datasets released by the UK Land Registry(https://use-land-property-data.service.gov.uk/).',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jwmock88/property-database/'
)

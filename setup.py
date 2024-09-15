from setuptools import setup

setup(
    name='property_project',
    version='0.1.0',  # Replace with the actual version if not importing
    py_modules=['build', 'search'],
    entry_points={
        'console_scripts': [
            'build=build:main',
            'search=search:main',
        ],
    },
    install_requires=[
        'pandas', 'tabulate',
        'requests', 'pyarrow', 'maskpass', 'fpdf2'
    ],
    author='Josh Mock',
    description='This project builds a database for searching the CCOD and OCOD datasets released by the UK Land Registry (https://use-land-property-data.service.gov.uk/).',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jwmock88/property-database/',
    license=open('LICENSE.md').read()
)

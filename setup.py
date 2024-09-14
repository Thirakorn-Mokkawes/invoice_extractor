from setuptools import setup, find_packages

setup(
    name="invoice_extractor",
    version="1.1.0", # Second release with new feature
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        "pdfplumber",
        "pytest" ,
        "plotly",
        "nbformat"
    ],
    entry_points={
        'console_scripts': [
            'invoice-extractor=invoice_extractor.extractor:main',
            'invoice-plot=plot.visualizations:main',
        ],
    },
    description="A tool to extract data from invoices and generate CSVs",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Thirakorn Mokkawes, PhD",
    author_email="thirakorn.mokkawes@gmail.com",  
    url="https://github.com/Thirakorn-Mokkawes/invoice_extractor",  
    license="MIT",  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

from setuptools import setup, find_packages

setup(
    name="invoice_extractor",
    version="0.1.0",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        "pdfplumber",
        "pytest"  # If needed for development
    ],
    entry_points={
        'console_scripts': [
            'invoice-extractor=invoice_extractor.extractor:main',
        ],
    },
    description="A tool to extract data from invoices and generate CSVs",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Thirakorn Mokkawes, PhD",
    author_email="thirakorn.mokkawes@gmail.com",  # Add your email here
    url="https://github.com/Thirakorn-Mokkawes/invoice_extractor",  # Update with your actual GitHub repo link
    license="MIT",  # Specify the MIT License
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

# Invoice Extractor

`invoice_extractor` is a Python package that extracts data from PDF invoices and generates CSV files. The tool is designed to handle invoice data extraction while respecting user privacy. Users can configure the tool to hide sensitive information such as customer account numbers and addresses in the CSV output.

## Features
- Extracts key invoice details such as customer account, invoice number, total amount, meter readings, and usage details.
- Generates a structured CSV file from the extracted data.
- Allows optional exclusion of sensitive fields (`customer_account`, `customer_address`) for privacy.
- Provides an easy-to-use command-line interface (CLI) for batch processing of invoices.
- Provides flexible testing framework using `pytest`.

## Requirements
- Python 3.6 or later
- Required packages: `pdfplumber`, `reportlab`, `pytest`

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Thirakorn-Mokkawes/invoice_extractor.git
    ```

2. Navigate to the project directory:
    ```bash
    cd invoice_extractor
    ```

3. Install the package:
    ```bash
    pip install .
    ```
## Uninstallation

```bash
pip uninstall invoice_extractor 
```
## Usage

### Command-Line Interface (CLI)

Once installed, you can run the tool from the command line using the `invoice-extractor` command.

```bash
invoice-extractor <input_directory> <output_directory> --show_customer_account --show_customer_address
```

- **input_directory**: Directory containing the PDF invoices.
- **output_directory**: Directory to save the CSV output.
- **--show_customer_account**: Optional flag to include the customer account in the output.
- **--show_customer_address**: Optional flag to include the customer address in the output.

### Example:
```bash
invoice-extractor ./invoices ./output --show_customer_account --show_customer_address
```
This command processes all the PDF files in the `./invoices` directory and saves the results to the `./output` directory. It includes both the customer account number and the customer address in the CSV output.

### Importing in Python or Jupyter Notebooks

You can also import `invoice_extractor` and use it within a Python script or Jupyter notebook.

```python
from invoice_extractor.extractor import InvoiceExtractor

# Example usage in a notebook
pdf_path = "path_to_pdf_invoice.pdf"
extractor = InvoiceExtractor(pdf_path)
invoice_data = extractor.extract_data()

print(invoice_data)
```

## Testing

The project includes a test suite to ensure the functionality of the invoice extractor. To run the tests, ensure you have `pytest` and `pytest-cov` installed. You can install the test dependencies using:

```bash
pip install pytest pytest-cov
```

### Testing Instructions:

1. **Add your own sample PDFs**:
   You need to place your own `sample_invoice.pdf` and `invalid_invoice.pdf` in the `tests/sample_data/` directory.

2. **Run the tests**:
   ```bash
   pytest --cov=invoice_extractor
   ```

   If you do not provide the necessary PDF files, the tests related to invoice extraction will be skipped.

### Example of Skipped Test Output:

```plaintext
SKIPPED [1] test_extractor.py:22: sample_invoice.pdf not found. Please add it to the sample_data directory.
```

### Coverage Report

You can also generate a coverage report to see how much of your code is covered by tests:

```bash
pytest --cov=invoice_extractor -rs
```

## Privacy

This tool provides options to protect sensitive information:

- **Customer Account**: You can choose to exclude the customer account number from the CSV output by omitting the `--show_customer_account` flag.
- **Customer Address**: You can choose to exclude the customer address by omitting the `--show_customer_address` flag.

Make sure that you respect the privacy of the data you are working with. When contributing to this project, use mock data or anonymized data in tests and examples.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or need support, feel free to open an issue on the [GitHub repository](https://github.com/Thirakorn-Mokkawes/invoice_extractor) or contact the author.

**Thirakorn Mokkawes, PhD**  
Email: thirakorn.mokkawes@gmail.com

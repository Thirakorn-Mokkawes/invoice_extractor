import os
import pytest
from invoice_extractor.extractor import InvoiceExtractor, save_to_csv  # Import save_to_csv
from datetime import datetime

@pytest.fixture
def sample_pdf_file():
    """Fixture to provide the path to a sample PDF file."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "sample_data/sample_invoice.pdf"))

def test_extract_data_valid(sample_pdf_file):
    """Test extraction of data from a valid invoice."""
    extractor = InvoiceExtractor(sample_pdf_file)
    invoice_data = extractor.extract_data()

    assert invoice_data is not None
    assert "printed_date" in invoice_data
    assert "total_amount_baht" in invoice_data
    assert "subtotal_baht" in invoice_data  # Ensure the field exists
    assert invoice_data["subtotal_baht"] is not None  # Check that it is not None

def test_sorting_by_printed_date():
    """Test if sorting by printed date works correctly."""
    data = [
        {"printed_date": "01-09-2023", "total_amount_baht": "3000.00"},
        {"printed_date": "01-08-2023", "total_amount_baht": "4000.00"},
    ]
    
    sorted_data = sorted(data, key=lambda x: datetime.strptime(x['printed_date'], "%d-%m-%Y"))
    assert sorted_data[0]["printed_date"] == "01-08-2023"
    assert sorted_data[1]["printed_date"] == "01-09-2023"

def test_save_to_csv(tmpdir):
    """Test saving data to CSV."""
    output_dir = tmpdir.mkdir("output")
    data = [
        {"printed_date": "01-09-2023", "total_amount_baht": "3000.00", "subtotal_baht": "2900.00"},
        {"printed_date": "01-08-2023", "total_amount_baht": "4000.00", "subtotal_baht": "3800.00"},
    ]

    # Call save_to_csv
    save_to_csv(data, str(output_dir), "test_invoice.csv")

    output_file = os.path.join(output_dir, "test_invoice.csv")
    assert os.path.exists(output_file)

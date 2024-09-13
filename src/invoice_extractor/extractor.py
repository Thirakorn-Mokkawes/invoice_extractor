import pdfplumber
import re
import csv
import os
import logging
import argparse
from datetime import datetime
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dictionary for converting Thai months to numeric values
thai_months = {
    "มกราคม": "01", "กุมภาพันธ์": "02", "มีนาคม": "03", "เมษายน": "04",
    "พฤษภาคม": "05", "มิถุนายน": "06", "กรกฎาคม": "07", "สิงหาคม": "08",
    "กันยายน": "09", "ตุลาคม": "10", "พฤศจิกายน": "11", "ธันวาคม": "12"
}


class InvoiceExtractor:
    """A class responsible for extracting invoice data from a PDF file."""

    def __init__(self, pdf_path: str):
        """
        Initialize the InvoiceExtractor with the path to the PDF file.

        Args:
            pdf_path (str): The path to the PDF file.
        """
        self.pdf_path = pdf_path
        self.data = self._initialize_data()

    def _initialize_data(self) -> Dict[str, Optional[str]]:
        """Initialize the dictionary to hold the extracted invoice data."""
        return {
            "printed_date": None,
            "printed_time": None,
            "customer_account": None,
            "invoice_number": None,
            "total_amount_baht": None,
            "due_date": None,
            "customer_address": None,
            "pea_code": None,
            "mru": None,
            "meter_number": None,
            "meter_type": None,
            "meter_reading_date": None,
            "billing_period": None,
            "voltage_level": None,
            "multiplier": None,
            "recent_reading": None,
            "previous_reading": None,
            "consumption_units": None,
            "usage_1_150_units": None,
            "usage_1_150_baht_per_unit": None,
            "usage_1_150_total_baht": None,
            "usage_151_400_units": None,
            "usage_151_400_baht_per_unit": None,
            "usage_151_400_total_baht": None,
            "usage_over_401_units": None,
            "usage_over_401_baht_per_unit": None,
            "usage_over_401_total_baht": None,
            "total_usage_units": None,
            "service_charge_baht": None,
            "total_based_amount_baht": None,
            "base_amount_baht": None,
            "ft_adjustment_baht": None,
            "subtotal_baht": None,
            "vat_percent": None,
            "vat_amount_baht": None,
            "total_baht": None,
            "grand_total_baht": None,
        }

    def extract_text(self) -> str:
        """
        Extract text from the PDF file.

        Returns:
            str: The extracted text from the PDF.
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                full_text = ''.join([page.extract_text() for page in pdf.pages])
            logging.info(f"Successfully extracted text from {self.pdf_path}")
            return full_text
        except Exception as e:
            logging.error(f"Failed to extract text from {self.pdf_path}: {e}")
            return ""

    def is_valid_invoice(self, text: str) -> bool:
        """
        Check if the PDF contains key markers identifying it as a valid invoice.

        Args:
            text (str): The extracted text from the PDF.

        Returns:
            bool: True if the PDF contains the required markers, otherwise False.
        """
        required_keywords = ["เลขที่ใบแจ้งค่าไฟฟ้า", "PEA Code", "จำนวนเงิน"]
        for keyword in required_keywords:
            if keyword not in text:
                logging.warning(f"{self.pdf_path} does not match the expected invoice format.")
                return False
        return True

    def extract_data(self) -> Optional[Dict[str, Optional[str]]]:
        """Run all extraction methods and return the structured data if the PDF is valid."""
        text = self.extract_text()
        if not self.is_valid_invoice(text):
            return None

        self._extract_printed_date(text)
        self._extract_ca_number(text)
        self._extract_invoice_number(text)
        self._extract_total_amount(text)
        self._extract_due_date(text)
        self._extract_address(text)
        self._extract_pea_code_section(text)
        self._extract_usage_data(text)
        self._extract_traffic_and_amounts(text)
        self._extract_service_charge_and_totals(text)  # Pass 'text' as argument here

        self._calculate_total_usage_units()

        return self.data


    def _extract_printed_date(self, text: str):
        """Extract printed date and time from the invoice text."""
        match = re.search(r"\*Printed\s*:\s*(\d{2}-\d{2}-\d{4})\s*(\d{2}:\d{2}:\d{2})", text)
        if match:
            self.data["printed_date"] = match.group(1)
            self.data["printed_time"] = match.group(2)
            logging.info(f"Extracted Printed Date: {self.data['printed_date']} | Time: {self.data['printed_time']}")

    def _extract_ca_number(self, text: str):
        """Extract the customer account number from the invoice text."""
        match = re.search(r"หมายเลขผู้ใช้ไฟฟ้า\s*(\d+)", text)
        if match:
            self.data["customer_account"] = match.group(1)
            logging.info(f"Extracted Customer Account: {self.data['customer_account']}")

    def _extract_invoice_number(self, text: str):
        """Extract the invoice number from the invoice text."""
        match = re.search(r"เลขที่ใบแจ้งค่าไฟฟ้า\s*(\d+)", text)
        if match:
            self.data["invoice_number"] = match.group(1)
            logging.info(f"Extracted Invoice Number: {self.data['invoice_number']}")

    def _extract_total_amount(self, text: str):
        """Extract the total amount from the invoice text."""
        match = re.search(r"จำนวนเงิน\s*\(บาท\)\s*([\d,]+\.\d+)", text)
        if match:
            self.data["total_amount_baht"] = match.group(1)
            logging.info(f"Extracted Total Amount (Baht): {self.data['total_amount_baht']}")

    def _extract_due_date(self, text: str):
        """Extract the due date from the invoice text."""
        match = re.search(r"วันที่ครบกำหนดค่าไฟฟ้าเดือนปัจจุบัน\s*(\d+)\s*(\S+)\s*(\d+)", text)
        if match:
            day, thai_month, thai_year = match.groups()
            month = thai_months.get(thai_month, "01")  # Convert Thai month to numeric
            year = str(int(thai_year) - 543)  # Convert Thai Buddhist year to Gregorian year
            formatted_date = f"{day}-{month}-{year}"
            self.data["due_date"] = formatted_date
            logging.info(f"Extracted Due Date: {self.data['due_date']}")

    def _extract_address(self, text: str):
        """Extract the customer address from the invoice text."""
        match = re.search(r"สถานที่ใช้ไฟฟ้า\s*(.+?)\s*Due Date", text)
        if match:
            self.data["customer_address"] = match.group(1)
            logging.info(f"Extracted Customer Address: {self.data['customer_address']}")

    def _extract_pea_code_section(self, text: str):
        """Extract PEA code and related meter information from the invoice text."""
        pea_code_marker = re.search(r"PEA Code MRU PEA No. Type Meter Reading Date Bill Period Voltage Level Multi", text)
        if pea_code_marker:
            next_line_match = re.search(r"PEA Code MRU PEA No. Type Meter Reading Date Bill Period Voltage Level Multi\s*\n(.+)", text)
            if next_line_match:
                values = next_line_match.group(1).strip().split()
                if len(values) >= 8:
                    self.data["pea_code"] = values[0]
                    self.data["mru"] = values[1]
                    self.data["meter_number"] = values[2]
                    self.data["meter_type"] = values[3]
                    self.data["meter_reading_date"] = values[4]
                    self.data["billing_period"] = values[5]
                    self.data["voltage_level"] = " ".join(values[6:8])
                    self.data["multiplier"] = values[8] if len(values) > 8 else "-"
                    logging.info(f"Extracted PEA Code and Meter Info: {self.data}")

    def _extract_usage_data(self, text: str):
        """Extract the recent reading, previous reading, and consumption units from the invoice text."""
        match = re.search(r"พลังงานไฟฟ้า\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)", text)
        if match:
            self.data["recent_reading"] = match.group(1)
            self.data["previous_reading"] = match.group(2)
            self.data["consumption_units"] = match.group(3)
            logging.info(f"Extracted Usage Data: {self.data['recent_reading']} (Recent), {self.data['previous_reading']} (Previous), {self.data['consumption_units']} (Consumption)")

    def _extract_traffic_and_amounts(self, text: str):
        """Extract usage traffic and associated amounts from the invoice text."""
        traffic_matches = [
            (r"\(หน่วยที่ 1-150\)\s*(\d+)\s*หน่วย\s*([\d,]+\.\d+)\s*([\d,]+\.\d+)", "usage_1_150_units", "usage_1_150_baht_per_unit", "usage_1_150_total_baht"),
            (r"\(หน่วยที่ 151-400\)\s*(\d+)\s*หน่วย\s*([\d,]+\.\d+)\s*([\d,]+\.\d+)", "usage_151_400_units", "usage_151_400_baht_per_unit", "usage_151_400_total_baht"),
            (r"\(หน่วยที่ 401 เป็นต้นไป\)\s*(\d+)\s*หน่วย\s*([\d,]+\.\d+)\s*([\d,]+\.\d+)", "usage_over_401_units", "usage_over_401_baht_per_unit", "usage_over_401_total_baht")
        ]

        for pattern, traffic, baht_per_unit, amount in traffic_matches:
            match = re.search(pattern, text)
            if match:
                self.data[traffic] = match.group(1)
                self.data[baht_per_unit] = match.group(2)
                self.data[amount] = match.group(3)
                logging.info(f"Extracted {traffic} Data: {self.data[traffic]} units, {self.data[baht_per_unit]} Baht/unit, {self.data[amount]} Baht total")

    def _extract_service_charge_and_totals(self, text: str):
        """Extract the service charge, total based amount, VAT, and grand total from the invoice text."""
        
        # Extract Service Charge
        service_charge_match = re.search(r"ค่าบริการรายเดือน\s*\(Service Charge\)\s*([\d,]+\.\d+)", text)
        if service_charge_match:
            self.data["service_charge_baht"] = service_charge_match.group(1)
            logging.info(f"Extracted Service Charge: {self.data['service_charge_baht']} Baht")

        # Extract Total Based Amount
        total_based_amount_match = re.search(r"รวมเงินค่าไฟฟ้าฐาน\s*\(Total Based Amount\)\s*([\d,]+\.\d+)", text)
        if total_based_amount_match:
            self.data["total_based_amount_baht"] = total_based_amount_match.group(1)
            logging.info(f"Extracted Total Based Amount: {self.data['total_based_amount_baht']} Baht")

        # Extract Base Amount
        base_amount_match = re.search(r"เงินค่าไฟฟ้าฐาน\s*\(Based Amount\)\s*([\d,]+\.\d+)", text)
        if base_amount_match:
            self.data["base_amount_baht"] = base_amount_match.group(1)
            logging.info(f"Extracted Base Amount: {self.data['base_amount_baht']} Baht")

        # Extract Ft Adjustment
        ft_adjustment_match = re.search(r"ค่า Ft.*=\s*([\d,]+\.\d+)\s*บาท/หน่วย\s*([\d,]+\.\d+)", text)
        if ft_adjustment_match:
            self.data["ft_adjustment_baht"] = ft_adjustment_match.group(2)
            logging.info(f"Extracted Ft Adjustment: {self.data['ft_adjustment_baht']} Baht")

        # Extract Subtotal
        subtotal_match = re.search(r"รวมเงินค่าไฟฟ้า\s*\(Sub Total\)\s*([\d,]+\.\d+)", text)
        if subtotal_match:
            self.data["subtotal_baht"] = subtotal_match.group(1)
            logging.info(f"Extracted Subtotal: {self.data['subtotal_baht']} Baht")

        # Extract VAT Percent and Amount
        vat_match = re.search(r"ภาษีมูลค่าเพิ่ม\s*(\d+\.\d+)\s*%\s*\(VAT\)\s*([\d,]+\.\d+)", text)
        if vat_match:
            self.data["vat_percent"] = vat_match.group(1)
            self.data["vat_amount_baht"] = vat_match.group(2)
            logging.info(f"Extracted VAT: {self.data['vat_percent']}%, {self.data['vat_amount_baht']} Baht")

        # Extract Total Amount
        total_match = re.search(r"รวมเงินค่าไฟฟ้าเดือนปัจจุบัน\s*\(Total\)\s*([\d,]+\.\d+)", text)
        if total_match:
            self.data["total_baht"] = total_match.group(1)
            logging.info(f"Extracted Total Amount: {self.data['total_baht']} Baht")

        # Extract Grand Total
        grand_total_match = re.search(r"รวมเงินทั้งสิ้น\s*\(Grand Total\)\s*([\d,]+\.\d+)", text)
        if grand_total_match:
            self.data["grand_total_baht"] = grand_total_match.group(1)
            logging.info(f"Extracted Grand Total: {self.data['grand_total_baht']} Baht")

    def _calculate_total_usage_units(self):
        """Sum all usage units to calculate the total usage."""
        try:
            usage_1_150 = float(self.data.get("usage_1_150_units", 0))
            usage_151_400 = float(self.data.get("usage_151_400_units", 0))
            usage_over_401 = float(self.data.get("usage_over_401_units", 0))

            self.data["total_usage_units"] = usage_1_150 + usage_151_400 + usage_over_401
            logging.info(f"Total Usage Units: {self.data['total_usage_units']}")
        except ValueError as e:
            logging.error(f"Error calculating total usage for {self.pdf_path}: {e}")


def save_to_csv(all_invoice_data: List[Dict[str, Optional[str]]], output_directory: str, csv_filename: str,
                show_customer_account: bool = True, show_customer_address: bool = True):
    """Save extracted invoice data to a CSV file."""
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    csv_file = os.path.join(output_directory, csv_filename)

    if not all_invoice_data:
        logging.warning("No valid invoices found to save.")
        return

    # Sort by printed_date (convert it to datetime for sorting)
    for data in all_invoice_data:
        # Convert only the date part of printed_date
        data['printed_date'] = datetime.strptime(data['printed_date'], "%d-%m-%Y")

    sorted_data = sorted(all_invoice_data, key=lambda x: x['printed_date'])

    # Adjust columns based on privacy flags
    csv_columns = list(sorted_data[0].keys())
    if not show_customer_account:
        csv_columns.remove("customer_account")
    if not show_customer_address:
        csv_columns.remove("customer_address")

    # Ensure missing values are handled
    for data in sorted_data:
        for column in csv_columns:
            if column not in data or data[column] is None:
                data[column] = ""  # Replace missing values with an empty string

    # Save data to CSV
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=csv_columns)
        writer.writeheader()
        for data in sorted_data:
            if not show_customer_account:
                data.pop("customer_account", None)
            if not show_customer_address:
                data.pop("customer_address", None)
            # Format printed_date as date only
            data['printed_date'] = data['printed_date'].strftime("%d-%m-%Y")
            writer.writerow(data)
    logging.info(f"Data saved to {csv_file}")


def get_pdf_files_from_directory(directory: str) -> List[str]:
    """
    Retrieve all PDF files from a given directory.

    Args:
        directory (str): Directory containing the PDF files.

    Returns:
        List[str]: List of paths to the PDF files.
    """
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    return [os.path.join(directory, f) for f in pdf_files]


def main():
    """Parse command-line arguments and process invoices."""
    parser = argparse.ArgumentParser(description="Extract data from invoices and generate CSVs.")
    parser.add_argument('input_directory', type=str, help="The directory containing the PDF files.")
    parser.add_argument('output_directory', type=str, help="The directory to save the output CSV.")
    parser.add_argument('--show_customer_account', action='store_true', help="Include customer account in the CSV.")
    parser.add_argument('--show_customer_address', action='store_true', help="Include customer address in the CSV.")

    args = parser.parse_args()
    process_invoices(args.input_directory, args.output_directory, args.show_customer_account, args.show_customer_address)


def process_invoices(input_directory: str, output_directory: str, show_customer_account: bool, show_customer_address: bool):
    """
    Process all PDF invoices in the input directory and generate a CSV with extracted data.

    Args:
        input_directory (str): Directory containing the PDF invoices.
        output_directory (str): Directory to save the CSV file.
        show_customer_account (bool): Whether to include customer account in the CSV.
        show_customer_address (bool): Whether to include customer address in the CSV.
    """
    all_invoice_data = []
    pdf_files = get_pdf_files_from_directory(input_directory)

    for pdf_file in pdf_files:
        extractor = InvoiceExtractor(pdf_file)
        invoice_data = extractor.extract_data()
        if invoice_data:
            all_invoice_data.append(invoice_data)

    save_to_csv(all_invoice_data, output_directory, "invoice_data.csv", show_customer_account, show_customer_address)


if __name__ == "__main__":
    main()

import pytest
import pdfplumber
import os
import json
from unittest import mock
from unittest.mock import patch, mock_open, MagicMock# Ensure you import your class correctly
import warnings
from ..report_reader import ReportReader
from agl_report_reader.report_reader import ReportReader
from ..anonymization.redact import cutoff_leading_text, cutoff_trailing_text


class MockPage:
    def __init__(self, text):
        self.text = text

    def extract_text(self):
        return self.text

class MockPDF:
    def __init__(self, pages=[]):
        self.pages = pages

    # Add the context manager methods
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
    
def mock_cutoff_trailing_text(text, flag_list):
    print(f"Text: {text}")
    print(f"Flag List: {flag_list}")
    for flag in flag_list:
        if flag in text:
            return text.split(flag)[0]
    return text



def test_check_folder_integrity():
    # Using mock to simulate os.path.isdir and os.makedirs behavior
    with patch("os.path.isdir", return_value=False) as mock_isdir, \
         patch("os.makedirs") as mock_makedirs:

        # Initialize the ReportReader
        reader = ReportReader(report_root_path="mock_path")
        
        # Ensure os.makedirs was called to create missing directories
        assert mock_makedirs.called

        # Check the method's return value
        assert reader.check_folder_integrity() == False

        # Modify mock to simulate directory existence
        mock_isdir.return_value = True
        assert reader.check_folder_integrity() == True

def test_get_new_reports():
    # Mocking os.listdir to return a list of files
    mock_files = ["report1.pdf", "report2.pdf", "not_a_report.txt"]

    with patch("os.listdir", return_value=mock_files), \
         patch("os.path.isdir", return_value=True), \
         patch("os.makedirs"):
        
        # Initialize the ReportReader
        reader = ReportReader(report_root_path="mock_path")

        # Expected result only contains .pdf files
        expected = ["mock_path/import/new/report1.pdf", "mock_path/import/new/report2.pdf"]
        assert reader.get_new_reports() == expected


def test_read_pdf():
    # Setup mock data
    mock_pdf_content = "Sample text from PDF."
    mock_pdf_path = "/mock/path/to/report.pdf"
    mock_new_path = "/mock/path/to/in_progress/report.pdf"
    mock_metadata = {
        "original_filename": "mock_original_filename.pdf",
        "new_filename": "mock_new_filename.txt",
        # ... Add other mock metadata key-value pairs as needed ...
    }

    # Mock a PDF page with extract_text method
    mock_page = MagicMock(spec=pdfplumber.page.Page)
    mock_page.extract_text.return_value = mock_pdf_content
    mock_page.text = "Sample Text from PDF"
    
    # Mock pdfplumber.open to return a mock PDF object with the pages attribute
    mock_pdf = MagicMock(pages=[mock_page])

    with patch("pdfplumber.open", return_value=mock_pdf), \
         patch("os.path.isdir", return_value=True), \
         patch.object(ReportReader, "move_report_to_in_progress", return_value=mock_new_path), \
         patch.object(ReportReader, "extract_report_meta", return_value=mock_metadata):

        # Initialize the ReportReader and test the read_pdf method
        reader = ReportReader(report_root_path="mock_pdf_path")
        extracted_text = reader.read_pdf("mock_pdf_path")

        # Assertion checks
        assert extracted_text == mock_pdf_content

        # Optional: Print out debugging information
        print(f"Expected Text: {mock_pdf_content}")
        print(f"Extracted Text: {extracted_text}")

        
        
def test_basic_read_pdf():
    def open_side_effect(*args, **kwargs):
        print("[DEBUG] pdfplumber.open called with:", args, kwargs)
        return mock_pdf
    # Mock content
    mock_pdf_content = "Sample text from PDF."

    # Mock page with extract_text method
    mock_page = MagicMock()
    mock_page.extract_text.return_value = mock_pdf_content
    print("[DEBUG] Mock page extract_text return value:", mock_page.extract_text())

    # Mock PDF with pages attribute
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    print("[DEBUG] Number of pages in mock PDF:", len(mock_pdf.pages))

    # Patch pdfplumber.open to return mock_pdf
    with patch("pdfplumber.open", return_value=mock_pdf, side_effect=open_side_effect):
        # Initialize the ReportReader
        reader = ReportReader(report_root_path="mock_path")

        # Extract text using read_pdf
        extracted_text = reader.read_pdf("mock_pdf_path")
        print("[DEBUG] Extracted Text:", extracted_text)
        print("[DEBUG] Was extract_text called on mock page?", mock_page.extract_text.called)


        # Assertion
        assert extracted_text == mock_pdf_content

    print("[DEBUG] Test completed successfully!")
        
def test_read_pdf_with_real_file():
    # Path to the real PDF
    real_pdf_path = "test_files/Hello_World.pdf"
    
    # Expected content from the real PDF (adjust based on the actual content)
    expected_content = "Hello World"
    
    # Initialize the ReportReader
    reader = ReportReader(report_root_path="/Users/Maxhi/Python_Tools_AG_Lux/report_reader/agl-report-reader/agl_report_reader/test")     
    # Extract text from the real PDF
    extracted_text = reader.read_pdf(real_pdf_path)
    
    # Assertion checks
    assert extracted_text == expected_content, f"Expected '{expected_content}' but got '{extracted_text}'"
            
  
def test_partial_folder_integrity():
    # Simulate scenario where some folders exist but not all
    with patch("os.path.isdir", side_effect=[True, False]) as mock_isdir, \
         patch("os.makedirs") as mock_makedirs:
        
        reader = ReportReader(report_root_path="mock_path")
        assert mock_makedirs.called

def test_get_new_reports_ignores_non_pdf():
    # Mocking os.listdir to return a list of files
    mock_files = ["report1.txt", "not_a_report.doc", "report2.pdf"]
    
    with patch("os.listdir", return_value=mock_files):
        reader = ReportReader(report_root_path="mock_path")
        expected = ["mock_path/import/new/report2.pdf"]
        assert reader.get_new_reports() == expected

def test_read_invalid_pdf():
    with patch("os.pdfplumber.open", side_effect=Exception("Invalid PDF")):
        reader = ReportReader(report_root_path="mock_path")
        with pytest.raises(Exception, match="Invalid PDF"):
            reader.read_pdf("mock_path/import/new/invalid.pdf")

def test_read_pdf_no_text():
    with patch("os.pdfplumber.open") as mock_open:
        mock_open.return_value.pages = []
        reader = ReportReader(report_root_path="mock_path")
        assert reader.read_pdf("mock_path/import/new/no_text.pdf") == ""

def test_move_report_to_in_progress():
    with patch("os.rename") as mock_rename:
        reader = ReportReader(report_root_path="mock_path")
        new_path = reader.move_report_to_in_progress("mock_path/import/new/report1.pdf")
        mock_rename.assert_called_once_with("mock_path/import/new/report1.pdf", "mock_path/import/tmp/report1.pdf")
        assert new_path == "mock_path/import/tmp/report1.pdf"

def test_extract_report_meta_patient_info():
    reader = ReportReader(report_root_path="mock_path")
    sample_text = "Some text\nPatient: John Doe\nMore text"
    metadata = reader.extract_report_meta(sample_text, "mock_path/import/new/report1.pdf")
    assert metadata.get("patient_name") == "John Doe"

def test_process_report_side_effects():
    # Mock functions that have side effects like file creation
    with patch("os.open", mock_open()), \
         patch("os.json.dump"), \
         patch("os.rename"):
        
        reader = ReportReader(report_root_path="mock_path")
        result, anon_text, meta = reader.process_report("mock_path/import/new/report1.pdf")
        
        assert result == True
        assert anon_text is not None
        assert meta is not None



def test_extract_report_meta_patient_info():
    # Sample text and flags
    text = "Patient: John Doe, Male, Age 45\nEndoscope: Model XYZ\nExaminer: Dr. Smith"
    patient_flag = "Patient:"
    endoscope_flag = "Endoscope:"
    examiner_flag = "Examiner:"

    # Mock the utility and helper functions
    with patch('agl_report_reader.utils.get_line_by_flag', return_value="Patient: John Doe, Male, Age 45"), \
        patch('agl_report_reader.anonymization.patient_data.extract_patient_info', return_value={'name': 'John Doe', 'gender': 'Male', 'age': 45}):
        
        meta = extract_report_meta(text, patient_flag, endoscope_flag, examiner_flag)
        assert meta['patient']['name'] == 'John Doe'
        assert meta['patient']['gender'] == 'Male'
        assert meta['patient']['age'] == 45
        
def test_process_new_reports_workflow():
    # Text with a flag
    mock_text = "This is some content. Gerät: END This is some trailing text.________________"

    # Create an instance of the ReportReader class
    reader = ReportReader(report_root_path="mock_path")

    # Create mock PDF with the specified text
    mock_pdf_with_flag = MockPDF([MockPage(mock_text)])

    # Mock the instance method get_new_reports for this instance
    # and also mock os.rename, pdfplumber.open, and the methods from redact.py
    with patch.object(reader, 'get_new_reports', return_value=["mock_path/import/new/report1.pdf"]), \
         patch('os.rename'), \
         patch('pdfplumber.open', return_value=mock_pdf_with_flag), \
         patch('agl_report_reader.anonymization.redact.cutoff_leading_text', return_value="mocked_leading_text"), \
         patch('agl_report_reader.anonymization.redact.cutoff_trailing_text', side_effect=mock_cutoff_trailing_text):
        reader.process_new_reports()





            
def test_incorrect_flags():
    # Define the flags and a sample text that doesn't contain them
    upper_cut_off_flags = ['Gerät: ', '1. Unters.:']
    sample_text = "Some sample text that does not contain the expected flags."

    # Expect an exception when the flags aren't found in the text
    with pytest.raises(Exception, match="No cutoff leading text flag found in text."):
        with patch('agl_report_reader.anonymization.redact.cutoff_leading_text', side_effect=Exception("No cutoff leading text flag found in text.")):
            # Call the function with the sample text and flags
            processed_text = cutoff_leading_text(sample_text, upper_cut_off_flags)




def test_empty_directory():
    with patch("os.listdir", return_value=[]):
        reader = ReportReader(report_root_path="mock_path")
        assert reader.get_new_reports() == []

        
def test_invalid_file_path():
    # Testing behavior with an invalid file path
    reader = ReportReader(report_root_path="mock_path")
    with pytest.raises(FileNotFoundError):
        reader.read_pdf("nonexistent_path/report1.pdf")

def test_unexpected_file_format():
    # Testing behavior with an unexpected file format
    with patch("os.listdir", return_value=["report1.jpeg"]):
        reader = ReportReader(report_root_path="mock_path")
        assert reader.get_new_reports() == []

def test_check_folder_integrity_with_existing_folders():
    # Simulate scenario where all folders already exist
    with patch("os.path.isdir", return_value=True) as mock_isdir:
        reader = ReportReader(report_root_path="mock_path")
        assert reader.check_folder_integrity() == True

def test_move_report_to_imported():
    with patch("os.rename") as mock_rename:
        reader = ReportReader(report_root_path="mock_path")
        new_path = reader.move_report_to_imported("mock_path/import/tmp/report1.pdf")
        mock_rename.assert_called_once_with("mock_path/import/tmp/report1.pdf", "mock_path/import/imported/report1.pdf")
        assert new_path == "mock_path/import/imported/report1.pdf"

def test_extract_report_meta_no_match():
    reader = ReportReader(report_root_path="mock_path")
    sample_text = "Text that does not match any flags."
    metadata = reader.extract_report_meta(sample_text, "mock_path/import/new/report1.pdf")
    assert "new_filename" in metadata
    assert metadata["original_filename"] == "report1.pdf"

def test_process_report_file_creation():
    # Mock functions to check if files are being created
    mock_content_with_flags = "Some random content before the flag. Gerät: Actual content after the flag."

    with patch("os.open", mock_open()) as m, \
         patch.object(ReportReader, "read_pdf", return_value=mock_content_with_flags), \
         patch("os.rename", return_value=None):

        reader = ReportReader(report_root_path="mock_path")
        
        with pytest.raises(Exception, match="No cutoff trailing text flag found in text."):
            reader.process_report("mock_path/import/new/report1.pdf")


def test_report_with_no_flags():
    # Test behavior when no flags are present in the report text
    reader = ReportReader(report_root_path="mock_path")

    mock_pdf_path = "mock_path/import/new/report1.pdf"

    # Mock the behavior of reading the PDF to return the sample text
    with mock.patch.object(reader, "read_pdf", return_value="This report has none of the expected flags."):

        # Mock the os.rename to avoid moving files
        with mock.patch("os.rename", return_value=None):

            # Expect the specific exception
            with pytest.raises(Exception, match="No cutoff leading text flag found in text."):

                reader.process_report(mock_pdf_path)



def test_mock_file_system_operations():
    # Define a custom open function to conditionally mock
    def conditional_mock_open(path, *args, **kwargs):
        if "nam_dict.txt" in path:
            return original_open(path, *args, **kwargs)
        
        if "report1.pdf" in path:
            mock_file = mock_file_data(path, *args, **kwargs)
            mock_file.seek.return_value = 0
            mock_file.tell.return_value = 0
            return mock_file
        
        return mock_file_data(path, *args, **kwargs)


    original_open = open
    mock_file_data = mock_open(read_data=b"mock_file_content")


    with patch("os.rename") as mock_rename, \
        patch("builtins.open", side_effect=conditional_mock_open) as mock_file, \
        patch("os.open", mock_file_data), \
        patch.object(ReportReader, "read_pdf", return_value="Gerät: mocked_pdf_content________________") as mock_read_pdf:  # Mock the read_pdf method

        reader = ReportReader(report_root_path="mock_path")
        reader.process_report("mock_path/import/new/report1.pdf")




def test_folder_creation_with_partial_existing_structure():
    # Define a generator function for the side_effect of os.path.isdir mock
    def isdir_side_effect(*args, **kwargs):
        responses = [True, False, True, False]
        if isdir_side_effect.counter < len(responses):
            result = responses[isdir_side_effect.counter]
            isdir_side_effect.counter += 1
            return result
        # Default behavior after the iterable is exhausted:
        return True  # or whatever default value you want

    isdir_side_effect.counter = 0

    # Simulate scenario where some folders already exist and others need to be created
    with patch("os.path.isdir", side_effect=isdir_side_effect) as mock_isdir, \
         patch("os.makedirs") as mock_makedirs:
        
        reader = ReportReader(report_root_path="mock_path")
        assert reader.check_folder_integrity() == True
        assert mock_makedirs.called



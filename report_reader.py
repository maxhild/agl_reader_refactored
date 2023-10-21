from .settings import DEFAULT_SETTINGS
from faker import Faker
import gender_guesser.detector as gender_detector
from typing import List
import os

import pdfplumber
from uuid import uuid4
import json
import os
from .anonymization import anonymize_report
from .extraction import extract_report_meta
import warnings


class ReportReader:
    '''
    The ReportReader class handles the processing and management of PDF medical reports.
    The main functionalities include ensuring data integrity, extracting metadata, 
    reading the content of PDFs, and anonymizing sensitive data within reports.
    
    Attributes:
        report_root_path (str): Root directory where reports are stored and processed.
        locale (str): Locale setting used for Faker and other functionalities.
        employee_first_names (List[str]): List of first names of employees used for anonymization.
        employee_last_names (List[str]): List of last names of employees used for anonymization.
        flags (List[str]): Flags that guide various processing steps.
        fake (Faker): Instance of Faker for data anonymization.
        gender_detector (gender_detector.Detector): Detector for guessing gender based on names.
        
    Methods:
        check_folder_integrity: Ensures that the necessary folders and subfolders exist for report processing.
        get_new_reports: Fetches new reports from the designated directory.
        read_pdf: Extracts text content from a PDF file.
        move_report_to_in_progress: Moves a report to an 'in progress' directory.
        move_report_to_imported: Moves a processed report to the 'imported' directory.
        extract_report_meta: Extracts metadata from a report.
        process_report: Processes a single report - from reading to anonymization.
        process_new_reports: Processes all new reports found in the designated directory.
    '''

    def __init__(
            self,
            #Root directory path where reports are stored and processed:
            report_root_path:str,
            #Locale setting used for Faker and other functionalities
            locale:str = DEFAULT_SETTINGS["locale"],
            #List of first names of employees used for anonymization.
            employee_first_names:List[str] = DEFAULT_SETTINGS["first_names"],
            #List of last names of employees used for anonymization.
            employee_last_names:List[str] = DEFAULT_SETTINGS["last_names"],
            #Flags that guide various processing steps.
            flags:List[str] = DEFAULT_SETTINGS["flags"],
    ):
        self.report_root_path = report_root_path

        self.locale = locale
        self.employee_first_names = employee_first_names
        self.employee_last_names = employee_last_names
        self.flags = flags
        self.fake = Faker(locale=locale)
        self.gender_detector = gender_detector.Detector(case_sensitive = True)
        self.check_folder_integrity()


    def check_folder_integrity(self):
        '''
        First checks if report root path is a folder. Then checks if the subfolders \
        import and working exist. Then checks if the corresponding subfolders \
        (import/new, import/tmp, import/imported, working/raw, working/metadata and working/anonymized exist. If not, they will be created.
        
        Returns:
            bool: True if folder structure is valid and ready, False otherwise.
        '''
        print("Checking folder integrity...")
        if not os.path.isdir(self.report_root_path):
            print(f"Error: {self.report_root_path} is not a directory.")
            return False
        
        self.new_report_dir = os.path.join(self.report_root_path, "import/new/")
        self.report_in_progress_dir = os.path.join(self.report_root_path, "import/tmp/")
        self.imported_report_dir = os.path.join(self.report_root_path, "import/imported/")

        self.raw_report_dir = os.path.join(self.report_root_path, "working/raw/")
        self.metadata_report_dir = os.path.join(self.report_root_path, "working/metadata/")
        self.anonymized_report_dir = os.path.join(self.report_root_path, "working/anonymized/")

        # make paths including parents if they don't exist yet
        os.makedirs(self.new_report_dir, exist_ok=True)
        os.makedirs(self.report_in_progress_dir, exist_ok=True)
        os.makedirs(self.imported_report_dir, exist_ok=True)
        os.makedirs(self.raw_report_dir, exist_ok=True)
        os.makedirs(self.metadata_report_dir, exist_ok=True)
        os.makedirs(self.anonymized_report_dir, exist_ok=True)

        print("Folder integrity check complete.")
        return True
        
    def get_new_reports(self):
        """
        Check self.new_report_dir for new reports. If there are new reports, \
        return a list of the full paths to the new reports. If there are no new reports, \
        return an empty list.
        
        Returns:
            List[str]: A list of full paths to the new reports. Returns an empty list if no new reports are found.

        """
        new_reports = []
        for file in os.listdir(self.new_report_dir):
            if file.endswith(".pdf"):
                new_reports.append(os.path.join(self.new_report_dir, file))
        
        return new_reports
    
    def read_pdf(self, pdf_path):
        '''
        Read pdf file using pdfplumber and return the raw text content.
        Args:
            pdf_path (str): The path to the PDF file to be read.
            
        Returns:
            str: Extracted raw text content from the PDF. Returns an empty string if the extraction fails.

        '''
        with pdfplumber.open(pdf_path) as pdf:
            # get the text content of the pdf file
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
            
            
            raw_text = text

        if not raw_text:
            warnings.warn(f"Could not read text from {pdf_path}.")
            return text
        
        return text
    
    def move_report_to_in_progress(self, pdf_path):
        '''
        Transfers a report from the 'new reports' directory to the 'in progress' directory.
        
        Args:
            pdf_path (str): Path to the report to be moved.
            
        Returns:
            str: New path of the moved report.
        '''
        filename = os.path.basename(pdf_path)
        os.rename(pdf_path, self.report_in_progress_dir + filename)
        new_path = self.report_in_progress_dir + filename

        return new_path

    def move_report_to_imported(self, pdf_path):
        '''
        Move a report from the report_in_progress_dir to the imported_report_dir.
        Args:
            pdf_path (str): Path to the report to be moved.
            
        Returns:
            str: New path of the moved report.
        '''
        filename = os.path.basename(pdf_path)
        os.rename(pdf_path, self.imported_report_dir + filename)
        new_path = self.imported_report_dir + filename

        return new_path
    
    
    def extract_report_meta(self, text, pdf_path):
        '''
        Extracts the metadata from a PDF, for example the patient info, the type of endoscope that was used and the name of the examiner into the report meta dictionary. 
        Using uuid4, a unique filename is generated. This new filename is then associated with the old filename from the pdf as well as the metadata.
        Args:
            text (str): Text content of the report.
            pdf_path (str): Path to the original PDF file.
            
        Returns:
            dict: Dictionary containing extracted metadata and associated filenames.
        '''
        report_meta = extract_report_meta(
            text,
            patient_info_line_flag = self.flags["patient_info_line"],
            endoscope_info_line_flag = self.flags["endoscope_info_line"],
            examiner_info_line_flag = self.flags["examiner_info_line"],
            gender_detector=self.gender_detector
        )
        filename = str(uuid4())
        report_meta["original_filename"] = os.path.basename(pdf_path)
        report_meta["new_filename"] = filename

        return report_meta

    def process_report(
        self,
        pdf_path,
        verbose = True
    ):
        '''
        Orchestrates the entire report processing pipeline:
            - Moves the report to the 'in progress' directory.
            - Reads the report's content.
            - Extracts metadata.
            - Anonymizes the content.
            - Saves the original and anonymized content in designated directories.
            - Moves the processed PDF to the 'imported' directory.
            
        Args:
            pdf_path (str): Path to the report to be processed.
            verbose (bool, optional): Flag to control the display of processing logs. Default is True.
            
        Returns:
            tuple: Contains a boolean indicating success, the anonymized text, and the extracted metadata.
        '''
        
        if verbose:
            print(f"Processing {pdf_path}")

        pdf_path = self.move_report_to_in_progress(pdf_path)

        if verbose:
            print(f"Moved to in_progress ( {pdf_path} )")

        text = self.read_pdf(pdf_path)
        report_meta = self.extract_report_meta(
            text,
            pdf_path
        )
        anonymized_text = anonymize_report(
            text = text,
            report_meta = report_meta,
            text_date_format = DEFAULT_SETTINGS["text_date_format"],
            lower_cut_off_flags=DEFAULT_SETTINGS["flags"]["cut_off_below"],
            upper_cut_off_flags=DEFAULT_SETTINGS["flags"]["cut_off_above"],
            locale = self.locale,
            first_names = self.employee_first_names,
            last_names = self.employee_last_names
        )


        filename = report_meta["new_filename"] # gets added in self.extract_report_meta

        raw_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        with open(self.raw_report_dir + raw_filename + ".txt", "w", encoding="utf-8") as f:
            f.write(text)

        # write the metadata to a json file
        with open(self.metadata_report_dir + filename + ".json", "w", encoding="utf-8") as f:
            json.dump(report_meta, f)

        # Write the anonymized text to a new text file
        with open(self.anonymized_report_dir + filename + ".txt", "w", encoding="utf-8") as f:
            f.write(anonymized_text)

        # move the pdf file to the imported folder
        pdf_path = self.move_report_to_imported(pdf_path)

        return True, anonymized_text, report_meta
    
    def process_new_reports(self, verbose = True):
        '''
        Handles the processing of all new reports found in the designated directory.
        
        Args:
            verbose (bool, optional): Flag to control the display of processing logs. Default is True.
            
        Returns:
            bool: True if processing is successful, otherwise False.        
        '''
        new_reports = self.get_new_reports()
        if verbose:
            print(f"Found {len(new_reports)} new reports.")
        for report in new_reports:
            self.process_report(report, verbose = verbose)
        
        return True
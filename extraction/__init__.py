from ..utils import get_line_by_flag
from .examination_data import extract_examination_info
from .patient_data import extract_patient_info
from .other_data import extract_endoscope_info

from icecream import ic

def extract_report_meta(
    text,
    patient_info_line_flag,
    endoscope_info_line_flag,
    examiner_info_line_flag,
    gender_detector = None,
    verbose = True
):
    """
    Extracts metadata from a medical report text based on provided flags.

    This function parses the provided text to extract information about the patient, endoscope, and examiner 
    using specified flags. The extracted metadata is returned as a dictionary.

    Parameters:
    - text (str): The medical report text from which metadata needs to be extracted.
    - patient_info_line_flag (str): A flag or pattern to identify the line containing patient information.
    - endoscope_info_line_flag (str): A flag or pattern to identify the line containing endoscope information.
    - examiner_info_line_flag (str): A flag or pattern to identify the line containing examiner information.
    - gender_detector (GenderDetector, optional): An instance of a gender detector for gender estimation based on names. Default is None.
    - verbose (bool, optional): If set to True, debugging information will be printed using the icecream library. Default is True.

    Returns:
    - dict: A dictionary containing the extracted metadata. The dictionary can have the keys:
        - 'patient': Information about the patient.
        - 'endoscope': Information about the endoscope used.
        - 'examiner': Information about the examiner.

    Example:
    ```
    report_text = "Patient: John Doe, Male, Age 45\nEndoscope: Model XYZ\nExaminer: Dr. Smith"
    meta = extract_report_meta(report_text, "Patient:", "Endoscope:", "Examiner:")
    print(meta)
    # Output: {'patient': {'name': 'John Doe', 'gender': 'Male', 'age': 45}, 'endoscope': 'Model XYZ', 'examiner': 'Dr. Smith'}
    ```

    Note:
    Ensure that the provided flags are unique to avoid misidentification of lines in the report.
    """
    report_meta = {}

    patient_info_line = get_line_by_flag(text, patient_info_line_flag)
    ic(patient_info_line)
    if patient_info_line:
        patient_info = extract_patient_info(patient_info_line, gender_detector)
        ic(patient_info)
        report_meta.update(patient_info)

    endoscope_info_line = get_line_by_flag(text, endoscope_info_line_flag)
    ic(endoscope_info_line)
    if endoscope_info_line:
        endoscope_info = extract_endoscope_info(endoscope_info_line)
        ic(endoscope_info)
        report_meta.update(endoscope_info)

    examiner_info_line = get_line_by_flag(text, examiner_info_line_flag)
    ic(examiner_info_line)
    if examiner_info_line:
        examiner_info = extract_examination_info(examiner_info_line)
        ic(examiner_info)
        report_meta.update(examiner_info)

    return report_meta
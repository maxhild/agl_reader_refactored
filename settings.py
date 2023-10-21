'''
This is a list of first names used for anonymization

'''

FIRST_NAMES = [
    "Markus",
    "Linhel",
    "Rainer",
    "Hans",
    "Anja",
    "Dorothea",
    "Doro",
    "Angelika",
    "Sven",
    "Theodor",
    "Alexander",
    "Mandy",
    "Kathrin",
    "Florian",
    "Philip",
    "Laura"
]
'''
This is a list of last names used for anonymization

'''

LAST_NAMES = [
    "Kozielski",
    "Reiter",
    "Purrer",
    "Kudlich",
    "Brand",
    "Weich",
    "Lux",
    "Meining",
    "Hann",
    "Retzbach",
    "Hose",
    "Henniger",
    "Weich",
    "Dela Cruz",
    "Wiese",
    "Weise",
    "Sodmann"
]
'''
These are string flags that indicate where specific pieces of information can be found in the report.
'''
PATIENT_INFO_LINE_FLAG = "Patient: "
ENDOSCOPE_INFO_LINE_FLAG = "Gerät: "
EXAMINER_INFO_LINE_FLAG = "1. Unters.:"

'''
A list of flags that might be used to truncate or anonymize the text below these lines in the report.
'''
CUT_OFF_BELOW_LINE_FLAG = "________________"

CUT_OFF_ABOVE_LINE_FLAGS = [
    ENDOSCOPE_INFO_LINE_FLAG,
    EXAMINER_INFO_LINE_FLAG,
]

CUT_OFF_BELOW_LINE_FLAGS = [
        CUT_OFF_BELOW_LINE_FLAG
    ]
'''
DEFAULT_SETTINGS:

A dictionary containing default settings and configurations:
locale: Specifies the locale (in this case, German) which might be used for date formatting, text processing, or generating fake data for anonymization.
first_names: Default list of first names.
last_names: Default list of last names.
text_date_format: Specifies the format for dates found within the text. For instance, '%d.%m.%Y' corresponds to dates formatted as "dd.mm.yyyy".
flags: A nested dictionary containing the flags used to identify specific lines or sections within the report for extraction, truncation, or anonymization.
'''
DEFAULT_SETTINGS = {
    "locale": "de_DE",
    "first_names": FIRST_NAMES,
    "last_names": LAST_NAMES,
    "text_date_format":'%d.%m.%Y',
    "flags": {
        "patient_info_line": PATIENT_INFO_LINE_FLAG,
        "endoscope_info_line": ENDOSCOPE_INFO_LINE_FLAG,
        "examiner_info_line": EXAMINER_INFO_LINE_FLAG,
        "cut_off_below": CUT_OFF_BELOW_LINE_FLAGS,
        "cut_off_above": CUT_OFF_ABOVE_LINE_FLAGS,
    }
}

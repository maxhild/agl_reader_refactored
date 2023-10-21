import re

def extract_endoscope_info(line):
    '''
    Using pattern matching with the re library, this function looks for the specification of the instrument used in the given endoscopy.
    Parameters:
    - line: str
        A line of text containing endoscope information.
    Returns:
        Dictionary assigning the key "endoscope" to the text found by the pattern matching, optimally the name of the instrument used.
    '''
    pattern = r"Gerät: ([\w\s-]+)"

    match = re.search(pattern, line)
    if match:
        endoscope = match.group(1).strip()
        return {"endoscope": endoscope}
    else:
        return None
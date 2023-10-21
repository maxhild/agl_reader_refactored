from datetime import datetime
import re

def extract_examination_info(line):
    """
    Extracts examiner and examination time information from a given text line.
    
    Parameters:
    - line: str
        A line of text containing examiner and examination time information.
        
    Returns:
    - info: dict
        A dictionary containing the extracted information: examiner's last name,
        examiner's first name, examination date (formatted as YYYY-MM-DD),
        and examination time in 24h format.
    
    Example:
    Input line: "1. Unters.: Dr. med. Lux, Thomas U-datum: 09.06.2023 09:30"
    Output: {'examiner_last_name': 'Dr. med. Lux', 'examiner_first_name': 'Thomas',
             'examination_date': '2023-06-09', 'examination_time': '09:30'}
    """
    
    # Define the regular expression pattern for matching the relevant fields
    pattern = r"Unters\.: ([\w\s\.]+), ([\w\s]+) U-datum: (\d{2}\.\d{2}\.\d{4}) (\d{2}:\d{2})"
    
    # Search for the pattern in the given line
    match = re.search(pattern, line)
    
    if match:
        examiner_last_name = match.group(1).strip()
        examiner_first_name = match.group(2).strip()
        
        # Convert the examination date to the format YYYY-MM-DD
        examination_date = datetime.strptime(match.group(3), '%d.%m.%Y').strftime('%Y-%m-%d')
        
        # Extract the examination time
        examination_time = match.group(4)
        
        info = {
            'examiner_last_name': examiner_last_name,
            'examiner_first_name': examiner_first_name,
            'examination_date': examination_date,
            'examination_time': examination_time
        }
        
        return info
    
    else:
        return None  # Return None if the pattern doesn't match
    

from typing import List

def cutoff_leading_text(text:str, flag_list:List[str]):
    """
    Truncate the leading portion of a given text up to the first occurrence of a flag from the provided list.
    
    This function searches for the first occurrence of any flag from the provided flag list in the text. 
    Once a flag is found, the function trims the leading portion of the text up to that flag and returns the rest.
    
    Parameters:
    - text (str): The input text that needs to be truncated.
    - flag_list (List[str]): A list of flags or markers. The function will truncate the text up to the first occurrence of any of these flags.
    
    Returns:
    - str: The truncated text.
    
    Raises:
    - Exception: If none of the flags in the flag list are found in the text.
    
    Example:
    ```
    text = "This is some leading text. START Here's the main content."
    truncated_text = cutoff_leading_text(text, ["START"])
    print(truncated_text)
    # Output: "START Here's the main content."
    ```
    """
    for flag in flag_list:
        search_result = text.find(flag)
        if search_result != -1:
            return text[search_result:]
        
    raise Exception("No cutoff leading text flag found in text.")

def cutoff_trailing_text(text:str, flag_list:List[str]):
    """
    Truncate the trailing portion of a given text from the last occurrence of a flag from the provided list to the end.
    
    This function searches for the last occurrence of any flag from the provided flag list in the text. 
    Once a flag is found, the function trims the trailing portion of the text from that flag to the end and returns the rest.
    
    Parameters:
    - text (str): The input text that needs to be truncated.
    - flag_list (List[str]): A list of flags or markers. The function will truncate the text from the last occurrence of any of these flags to the end.
    
    Returns:
    - str: The truncated text.
    
    Raises:
    - Exception: If none of the flags in the flag list are found in the text.
    
    Example:
    ```
    text = "Here's the main content. END This is some trailing text."
    truncated_text = cutoff_trailing_text(text, ["END"])
    print(truncated_text)
    # Output: "Here's the main content. "
    ```
    """
    for flag in flag_list:
        search_result = text.rfind(flag)
        if search_result != -1:
            return text[:search_result]
        
    raise Exception("No cutoff trailing text flag found in text.")
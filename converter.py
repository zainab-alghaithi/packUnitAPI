import logging
from typing import List
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def custom_char_to_number(input_str: str) -> List[int]:
    """
    Converts the encoded input string into a list of numbers according to these rules:
      - Letters 'a'-'z' are converted to 1-26.
      - '_' or '-' are converted to 0.
      - If a 'z' is found and has a following character, they are combined:
           • If the next character is '_' or '-', the value is 26 + 0.
           • If the next character is a letter, the value is 26 + (value of the letter).
    
    For example:
      "dz_a_aazzaaa" → [4, 26, 1, 0, 1, 1, 53, 1, 1]
    """
    result = []
    i = 0
    while i < len(input_str):
        char = input_str[i].lower()
        if char in ['_' ]:
            result.append(0)
            i += 1
        elif char == 'z' and (i + 1) < len(input_str):
            next_char = input_str[i + 1].lower()
            if next_char in ['_']:
                # "z" followed by "_"   becomes 26 + 0.
                result.append(26 + 0)
            elif 'a' <= next_char <= 'z':
                # "z" followed by a letter becomes 26 + (value of the letter)
                result.append(26 + (ord(next_char) - ord('a') + 1))
            else:
                result.append(26)
            i += 2  # Skip both 'z' and its following character.
        elif 'a' <= char <= 'z':
            result.append(ord(char) - ord('a') + 1)
            i += 1
        else:
            logger.warning(f"Skipping invalid character: {char}")
            i += 1
    return result

def parse_packages(values: List[int]) -> List[int]:
    """
    Groups the list of numbers into packages following a pointer algorithm:
      - The first number is the package count (i.e. how many measurement values follow).
      - Those measurement numbers are summed to form the package's total.
      - Then the pointer moves past those values and the process repeats.
    
    For example:
      Given values: [4, 26, 1, 0, 1, 1, 53, 1, 1]
      • Index 0: Count = 4 → Sum the next four numbers: 26 + 1 + 0 + 1 = 28.
      • Advance pointer by (1 + 4) → Next index becomes 5.
      • Then count = 1 → Sum the next 1 number: 53.
      • Then count = 1 → Sum the next 1 number: 1.
      
      Final result: [28, 53, 1]
    """
    packages = []
    i = 0
    while i < len(values):
        count = values[i]
        i += 1
        # If there are not enough values, default missing measurements to 0.
        if i + count > len(values):
            tail = values[i:] + [0]*(i + count - len(values))
        else:
            tail = values[i:i+count]
        pkg_sum = sum(tail)
        packages.append(pkg_sum)
        i += count
    return packages

def convert_measurement_string(input_str: str, mode: str = "lenient") -> List[int]:
    """
    Converts an encoded measurement input string into a list of package sums.
    
    The steps are:
      1. Convert the input string to a list of numbers using custom_char_to_number().
      2. Use pointer logic where the first number indicates how many measurement values to sum,
         then repeat with the next package.
    
    For example, for input "dz_a_aazzaaa" the process is:
      Custom conversion: [4, 26, 1, 0, 1, 1, 53, 1, 1]
      Packaging: [28, 53, 1]
    
    Returns:
        List[int]: A list of package sums.
    """
    input_str = input_str.strip()
    numbers = custom_char_to_number(input_str)
    packages = parse_packages(numbers)
    return packages
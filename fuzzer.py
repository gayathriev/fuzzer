import sys
import os
from pwn import *

import xml.etree.ElementTree as ET # Here for testing - will move to XML_fuzz
from json_fuzzer import json_fuzzer

BINARY_FOLDER = "binaries/"

if len(sys.argv) != 3:
    sys.exit("Usage: python3 fuzzer.py [binaryName] [sampleInput]")

binary_file = sys.argv[1]
print("Binary: " + binary_file)
input_file = sys.argv[2]
print("Input File: " + input_file)

binary = BINARY_FOLDER + binary_file
if not (os.path.isfile(binary)):
    sys.exit("Binary does not exist")

sample = BINARY_FOLDER + input_file
if not (os.path.isfile(sample)):
    sys.exit("Sample input does not exist")

'''
Test case - determine data type
Execute fuzzer for specific data type:
 1. Plaintext (multiline)
 2. JSON
 3. XML
 4. CSV
 5. JPEG
 6. ELF
 7. PDF
'''
with open(sample) as file:
    # If JSON, do JSON_fuzz else
    try:
        json_fuzzer(binary, sample)
    except Exception as e:
        print("=== JSON PANIKK ===")
        print(e)
        pass   
    # If XML, do XML_fuzz else
    try:
        file.seek(0)
        xmlObj = ET.parse(file)
    except Exception as e:
        pass # head to next case (CSV)
    # do XML_Fuzz
    
    # If CSV, do CSV_fuzz else
    
    # If JPEG, do JPEG_fuzz else
    
    # If ELF, do ELF_fuzz else
    
    # If PDF, do PDF_fuzz else
    
    # plaintxt_fuzz
    

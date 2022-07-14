import sys
import os
from support import detect
from pwn import *
from Harness import Harness

BINARY_FOLDER = "binaries/"
SEGFUALT_SIGNAL = -11

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

mode = detect(sample)
# make instance of fuzzer from detected mode

def run_fuzzer(self):
        """ start the fuzzing campaign """

        # exit handler
        signal(SIGINT, self.end_campaign)
        while True:
            inputs = # get from the correct fuzzer type (ex: )
            for input in inputs:
                response_number = harness.start_process(input)
                # temporarily halt on crash
                if (response_number == SEGFUALT_SIGNAL):
                    
                    # TODO - write unique crash files
                    exit()
                    



import io
import sys
import os
import random
import copy
import re
import PyPDF2
from pwn import *

MAX_BUF = 0x5000
FUZZ_INPUTS = ['null', '*', '%', '@', '$', '-', '+', ';', ':', 'true', 'false', '0', '%%', '%p', '%d', '%c', '%u', '%x', '%s', '%n', ' ']
KNOWN_INTS = [0, 1, 9, 256, 1024, 0x7F, 0xFF, 0x7FFF, 0xFFFF, 0x80, 0x8000, MAX_BUF]

# Reads pdf file and returns mutable pdfReader object
def read_pdf(filename):
    # creating a pdf file object
    pdfFileObj = open(filename, 'rb')
    
    # creating a pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    return (pdfReader, pdfFileObj)

# Returns cloned pdfWriter object
def clone_pdf(reader):
    pdfWriter = PyPDF2.PdfFileWriter()
    pdfWriter.clone_document_from_reader(reader)
    return pdfWriter

# Print content of pdfWriter in bytes
def print_pdf(writer):
    stream = io.BytesIO()
    writer.write(stream)
    result = stream.getvalue()
    print(len(result))
    stream.seek(0)
    stream.truncate(0)

# Return empty pdf
def empty_pdf():
    pdfWriter = PyPDF2.PdfFileWriter()
    return pdfWriter

# Return large pdf with MAX_BUF appended pages, up to 3 iterations
def large_pdf(reader):
    writer = clone_pdf(reader)
    page = writer.get_page(0)

    for x in range(3):
        for y in range(MAX_BUF):
            writer.add_page(page)
        yield writer

# Return input pdf without any images
def nullify_pdf_images(reader):
    writer = clone_pdf(reader)

    writer.remove_text()
    return writer

def generate_input(reader):
    # Empty pdf file
    print("testing empty")
    yield empty_pdf()

    print("testing no images")
    # Remove all images from pdf
    yield nullify_pdf_images(reader)

    # Original input file
    print("orginal")
    yield clone_pdf(reader)

    print("testing large")
    # Large pdf
    for x in large_pdf(reader):
        yield x

#################################
###     MAIN STUFF
#################################
def pdf_fuzzer(binary_file, input):
    pdf = read_pdf(binary_file)
    reader = pdf[0]
    file = pdf[1]

    for test in generate_input(pdf):
        yield test

    file.close()
pdf = read_pdf('example.pdf')
reader = pdf[0]
file = pdf[1]      

for test in generate_input(reader):
    print_pdf(test)



file.close()
from email import contentmanager
import io
import sys
import os
import random
import copy
import re
import PyPDF2
from pwn import *

MAX_BUF = 0x5000

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
    return result

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

# Return input pdf with format string injection
def edit_pdf(reader):
    writer = PyPDF2.PdfFileWriter()
    page = reader.pages[0]
    writer.add_page(page)

    stream = io.BytesIO()
    writer.write(stream)
    result = stream.getvalue()

    inject = b'(' + b'%s' * MAX_BUF + b')'
    new_pdf = re.sub(b'\((.*?)\)', inject, result)
    print(len(new_pdf))
    
    return new_pdf

# Return input pdfs with different types of  filters
def replace_filters(reader):
    filter_types = ["/FlateDecode", "/ASCIIHexDecode", "/ASCII85Decode", "/LZWDecode", "/RunLengthDecode", "/CCITTFaxDecode", "/JBIG2Decode", "/DCTDecode", "/JPXDecode", "/Crypt"]

    writer = clone_pdf(reader)
    pdf = print_pdf(writer)
    
    for type in filter_types:
        byte_str = b'/Filter ' + bytes(type, 'utf-8') + b'\n'
        new_pdf = re.sub(b'/Filter /.+\n', byte_str, pdf)
        yield new_pdf

def generate_input(reader):
    # Empty pdf file
    print("testing empty")
    yield print_pdf(empty_pdf())

    # Original input file
    print("testing orginal")
    yield print_pdf(clone_pdf(reader))

    print("testing replacing filter types")
    for x in replace_filters(reader):
        yield x
    
    print("testing edit pdf")
    # Remove all images from pdf
    yield edit_pdf(reader)

    print("testing large")
    # Large pdf
    for x in large_pdf(reader):
        yield print_pdf(x)

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
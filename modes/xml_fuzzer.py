import io
import sys
import os
import random
import copy
import xml
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring
import re
from support.log_crash import log_crash

from pwn import *

MAX_BUF = 0x500
FUZZ_INPUTS = ['null', '%s','*', '%', '@', '$', '-', '+', ';', ':', 'true', 'false', '0', '%%', '%n', ' ']
KNOWN_INTS = [0, 1, 9, 256, 1024, 0x7F, 0xFF, 0x7FFF, 0xFFFF, 0x80, 0x8000, MAX_BUF]

# Create random string from 0x20 to 0x7E from ascii table
def rand_str():
    start = 32
    end = 126
    str_len = random.randrange(0, MAX_BUF)
    output = ""
    for i in range(0, str_len):
        output += chr(random.randrange(start, end))
    return output

def tree_to_string(tree):
    return ET.tostring(tree)

def tree_to_bytes(tree):
    return bytes(tree_to_string(tree), 'utf-8')

def read_xml(filename):
    f = open(filename)
    root = ET.parse(f).getroot()
    return root

def span_child(child, xml):
    root = copy.deepcopy(xml)
    child = root.find(child.tag)
    for i in range(0, random.randint(50, 110)):
        root.append(copy.deepcopy(child))
    return root

def nest(xml):
    root = copy.deepcopy(xml)
    curr = root
    text_size = [1, 100, 1000, 10000, 100000, 1000000]
    for count in text_size:
        for i in range(100):
            curr = breed_child(curr, count)
        yield root

def breed_child(root, count):
    tag = 'a'
    child = ET.SubElement(root, tag)
    child.text = 'A' * count
    child.tail = '\n'
    return child

# Sets attribute value in tag to input
def set_tag(xml, tag, attr, input):
    root = copy.deepcopy(xml)
    for c in root.iter(tag):
        c.set(attr, input)
    return root

# Inject tags from tuple lists with generated input
# TODO: Clean up tuple_list, convert to attrib/tag loop
def inject_tag(xml, input):
    tuple_list = [('a', 'href'), ('link', 'href'), ('div', 'id'), ('div', 'class'), ('abbr', 'title'), ('source', 'src'), 
    ('source', 'type'), ('data', 'value'), ('datalist', 'id'), ('option', 'value'), ('input', 'list'), ('input', 'name'), 
    ('input', 'id'), ('label', 'for'), ('svg', 'width')]
    for tag in tuple_list:
        yield set_tag(xml, tag[0], tag[1], input)

# Inject input into text between all sets of tags
def inject_text(xml, input):
    root = copy.deepcopy(xml)
    for elem in root.iter():
        if type(elem.text) != str:
            continue
        if not elem.text.isspace():
            elem.text = input
    return root

# Injecting into XML
def inject(xml, text, mul = 1):
    if mul > 1024:
        text = text[:1]
    # Inject into tag
    for res in inject_tag(xml, (text * mul)):
        yield res
    # Inject into text
    yield inject_text(xml, (text * mul))

def fuzz_by_injection(xml):
    for x in FUZZ_INPUTS:
        for res in inject(xml, x):
            yield res
    for y in KNOWN_INTS:
        # Format Str
        for res in inject(xml, "%s", y):
            yield res
        # Raw Byte
        for res in inject(xml, "A", y):
            yield res
    for res in inject(xml, rand_str()):
        yield res

# Arithmetic: Increment all integer values from -35 to 35
def arithmetic(xml):
    xml_str = tree_to_string(xml).decode('utf-8')

    res = re.findall('[0-9]+', xml_str)
    
    for i in range(-35, 35):
        new_xml = xml_str
        for num in res:
            target = str(int(num) + i)
            new_xml = new_xml.replace(num, target)
            yield ET.fromstring(new_xml)

# Byte Flips: Flips bytes at a 5% chance for every byte in the XML payload, looped 30 times
def byte_flips(xml):
    xml_str = tree_to_string(xml).decode('utf-8')
    xml_bytes = bytearray(xml_str, 'utf-8')
    
    for x in range(0, len(xml_bytes)):
        copy = xml_bytes.copy()
        if random.randint(0, 20) == 1:
            copy[x] ^= random.getrandbits(7)
        res = bytes(copy)
        yield res

#################################
###     TEST
#################################
def test_payload(binary_file, xml):
    p = process('./' + binary_file)
    payload = xml
    p.send(payload)
    p.proc.stdin.close()

    exit_status = None
    while exit_status == None:
        p.wait()
        exit_status = p.returncode
    if (exit_status == -11):
        print("Program terminated: Check 'bad.txt' for output")
        log_crash(payload.decode("utf-8"))
        exit(0)
    
    p.close()

def generate_input(xml):
    # Empty input
    yield b''

    # Original input
    input = tree_to_string(xml)
    yield input
    
    # known int + overflow + fmt str injection
    for x in fuzz_by_injection(xml):
        input = tree_to_string(x)
        yield input

    # Add child to parent rand times
    for child in xml:
        mutated = span_child(child, xml)
        input = tree_to_string(mutated)
        yield input
    
    # Recursively add child to itself 100 times
    for x in nest(xml):
        input = tree_to_string(x)
        yield input
    
    # Arithmetic
    for x in arithmetic(xml):
        input = tree_to_string(x)
        yield input

    # Byte Flips
    for x in byte_flips(xml):
        yield x
    
#################################
###     MAIN STUFF
#################################
def xml_fuzzer(binary_file, input):
    print("============== running xml fuzzer ==============")
    xml = read_xml(input)
    for test in generate_input(xml):
        # Returns input string iteratively through yield
        yield test
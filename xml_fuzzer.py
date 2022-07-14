import io
import sys
import os
import random
import copy
import xml
import xml.etree.ElementTree as ET

from pwn import *

MAX_BUF = 0x100

def tree_to_string(tree):
    return ET.tostring(tree).decode()

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

def breed_child(child, parent, xml):
    root = copy.deepcopy(xml)
    parent = root.find(parent.tag)
    child = root.find(child.tag)
    _root = copy.deepcopy(child)

    for i in range(0, random.randint(50,100)):
        _child = copy.deepcopy(_root)
        _child.tag = str(random.randint(0,10000))
        _root.append(_child)
        _root = _root.find(_child.tag)

    parent.append(_root)

    return root

def bit_flip(byte):
    return byte ^ random.choice([1, 2, 4, 8, 16, 32, 64, 128])

def inject_overflow(xml):
    root = copy.deepcopy(xml)
    for c in root.iter('a'):
        c.set("href", "https://" + "A" * MAX_BUF + ".com")
    return root

def inject_fstring(xml):
    root = copy.deepcopy(xml)
    for c in root.iter('a'):
        c.set("href", "https://" + "%s" * MAX_BUF + ".com")
    return root

#################################
###     TEST
#################################
def test_payload(binary_file, xml):
    p = process('./' + binary_file)
    payload = bytes(xml, 'utf-8')
    # Hardcoded fread exit, fread not terminating otherwise
    payload += b'A' * (0x270e - len(payload))
    p.send(payload)
    mess = p.recvlines(2, timeout=0.2)
    print(mess)
    p.close()

def generate_input(xml):
    # Empty input
    print("empty")
    print("----------------------")
    yield ""

    # Original input
    print("original")
    print("----------------------")
    input = tree_to_string(xml)
    print(input)
    yield input

    # Add child to parent rand times
    print("breadthwise add")
    print("----------------------")
    for child in xml:
        yield ET.tostring(span_child(child, xml)).decode()

    # Recursively add random child to itself rand times
    print("depthwise add")
    print("----------------------")
    for parent in xml:
        for child in xml:
            yield ET.tostring(breed_child(child, parent, xml)).decode()

    # Inject fstring
    print("inject fstring")
    print("----------------------")
    input = tree_to_string(inject_fstring(xml))
    yield input

    # Overflow link
    print("overflow link")
    print("----------------------")
    input = tree_to_string(inject_overflow(xml))
    yield input

    # Content int overflow (2 ** 31)

    # Content int underflow (-2 ** 31)

    # Child name overflow

    # Child name fstring

    # Bit flips

    # Byte flips

    # Known ints

    # Repeated parts

    # Keyword extraction

    # Arithmetic

    # Coverage based mutations

    # Buffer overflow tag names

    # Buffer overflow tag properties

    # Tag Name to Format String

    # Tag Properties to Format String

    # Big print

    # Properties --> bad ints

    # Content --> bad ints

    # Bit shift

    # Node Shuffle

#################################
###     MAIN STUFF
#################################
def xml_fuzzer(binary_file, input):
    xml = read_xml(input)
    for test in generate_input(xml):
        try:
            test_payload(binary_file, test)
        except Exception as e:
            print(e)
        
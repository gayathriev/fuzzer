import random
import copy
import xml
import xml.etree.ElementTree as ET

from pwn import *

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

#################################
###     TEST
#################################
def test_payload(binary_file, xml):
    p = process('./' + binary_file)
    p.send(xml)
    mess = p.recvlines(2, timeout=0.1)
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
    yield ET.tostring(xml).decode()

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
            yield ET.tostring(span_child(child, xml)).decode()

    # Link overflow

    # Link fstring

    # Content int overflow (2 ** 31)

    # Content int underflow (-2 ** 31)

    # Child name overflow

    # Child name fstring


#################################
###     MAIN STUFF
#################################
def xml_fuzzer(binary_file, input, loops=10):
    xml = read_xml(input)
    for test in generate_input(xml):
        try:
            test_payload(binary_file, test)
        except Exception as e:
            print(e)
            
        
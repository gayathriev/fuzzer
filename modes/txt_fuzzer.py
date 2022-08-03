from random import randint, randrange
from pwn import cyclic
import sys
import os
import json
import copy
import random


GEN_MAX = 100
CHAR_MAX = 255
INT_MAX  = 4294967295
INT_MAX_SIGNED = 2147483648
BYTE_8_MAX = 18446744073709551615
INSTRUCTION_SIZE = 32

# read sameple file 
def read_txt(input_file):
    with open(input_file) as f:
        return f.readlines()


def large_negatives():
    """ Gen large negative integers """
    for i in range(0, 32):
        yield str(-(2 ** i))


def large_positives():
    """ Gen large negative integers """
    for i in range(0, 32):
        yield str(2 ** i)


# Implement format strings
def format_strings(data='', offset=1):
    """ Format string fuzzcases """
    yield data + f'%{offset}$p'
    yield data + f'%{offset}$n'
    yield data + f'%{offset}$d'
    yield data + f'%{offset}$s'
    yield data + f'%{offset}$x'
    yield data + f'%{offset}$@'
    yield data + f'%{offset}$hn'
    yield data + f'%{offset}hhn'
    yield data + f'%99999$n'
    yield data + f'%400$n'
    for modifier in range(32):
        yield data + f'%{2**modifier}$n'


# Implement cyclic payloads
def cyclic_gen():
    yield cyclic(100).decode()	
    yield cyclic(500).decode()
    yield cyclic(1000).decode()
    yield cyclic(4000).decode()
    yield cyclic(10000).decode()


def known_ints():
    yield '255'
    yield '4294967295'
    yield '2147483648'
    yield '18446744073709551615'
    yield str(0)
    yield str(-INT_MAX)
    yield str(-BYTE_8_MAX)
    yield str(-CHAR_MAX)
    yield str(INT_MAX + 1)
    yield str(CHAR_MAX + 1)


def bit_flip_values():
    yield 1
    yield 2
    yield 4
    yield 8
    yield 16
    yield 32
    yield 64
    yield 128
    yield 255

# keywords

# def pack_stream(bytes):
# 	""" pack csv list into string """
# 	return "".join(map(chr, bytes))


# byte flipss
def xor_bytes(bytes, index, value):
    prev_byte = bytes[index]
    bytes[index] ^= value
    yield pack_stream(bytes)
    bytes[index] = prev_byte


def xor_string(data):
	return ''.join(chr(ord(char) ^ 0xFF) for char in data)


def txt_fuzzer(binary_file, input_file):

    sample_txt = read_txt(input_file)
    perm_inputs = []

    # try cyclic payloads
    mutated_copy = copy.deepcopy(sample_txt)
    for chunk in cyclic_gen():
        mutated_copy.append(chunk)
        perm_inputs.append("".join(mutated_copy))
        #perm_inputs.append(chunk)

    # try format strings
    mutated_copy = copy.deepcopy(sample_txt)
    for fmtstring in format_strings():
        mutated_copy = copy.deepcopy(sample_txt)
        mutated_copy.append(fmtstring) 
        perm_inputs.append("".join(mutated_copy))
    
    
    # known integers
    for num in known_ints():
        mutation = copy.deepcopy(sample_txt)
        for line in range(len(mutation)):
            mutation = copy.deepcopy(sample_txt)
            mutation[line] = num + '\n'
            perm_inputs.append("".join(mutation))


    #append large negatives
    for negative in large_negatives():
        mutation = copy.deepcopy(sample_txt)
        for line in range(len(mutation)):
            mutation = copy.deepcopy(sample_txt)
            mutation[line] = negative + '\n'
            perm_inputs.append("".join(mutation))


    # append large positives
    for big_int in large_positives():
        mutation = copy.deepcopy(sample_txt)
        for line in range(len(mutation)):
            mutation = copy.deepcopy(sample_txt)
            mutation[line] = big_int + '\n'
            perm_inputs.append("".join(mutation))
    

    mutation = copy.deepcopy(sample_txt)
    for line in range(len(mutation)):
        mutation.append(xor_string(mutation[line]))
        perm_inputs.append("".join(mutation))
    
    mutation = copy.deepcopy(sample_txt)
    for line in range(len(mutation)):
        # append on newline
        mutation[line] = (xor_string(mutation[line]) + '\n')
        perm_inputs.append("".join(mutation))
        mutation = copy.deepcopy(sample_txt)
    
    # mutation = copy.deepcopy(sample_txt)
    # for line in range(len(mutation)):
    #     # prepend
    #     mutation.insert(0, xor_string(mutation[line]))
    #     perm_inputs.append("".join(mutation))


    # stream = list("".join(copy.deepcopy(sample_txt)).encode())
    # for line in range(len(stream)):
    #     # byte by byte
    #     for num in bit_flip_values():
    #         for mutation in xor_bytes(stream, line, num):
    #             perm_inputs.append(mutation)

    return perm_inputs
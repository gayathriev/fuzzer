from random import randint, randrange
from pwn import cyclic
import sys
import os
import json
import copy
import random


KNOWN_INTS = ['0','255', '256', '4294967295', '2147483648', '18446744073709551615', '-4294967295', '-18446744073709551615', 
'4294967296']

BIT_FLIP_VALS = [1, 2, 4, 8, 16, 32, 64, 128, 255]

# read sameple file 
def read_txt(input_file):
    with open(input_file) as f:
        return f.readlines()


def large_negatives():
    # Generate small numbers '32' for intruction size
    for i in range(0, 32):
        yield str(-(2 ** i))


def large_positives():
    # Generate large numbers '32' for intruction size
    for i in range(0, 32):
        yield str(2 ** i)


# Format string fuzz technique
def format_strings(data='', offset=1):
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
    for num in range(32):
        yield data + f'%{2**num}$n'


# Random cyclic payloads
def cyclic_gen():
    yield cyclic(100).decode()	
    yield cyclic(500).decode()
    yield cyclic(1000).decode()
    yield cyclic(4000).decode()
    yield cyclic(10000).decode()

# keywords

# def pack_stream(bytes):
# 	""" pack csv list into string """
# 	return "".join(map(chr, bytes))




# Byte flippinf
def xor_bytes(bytes, index, value):
    prev_byte = bytes[index]
    bytes[index] ^= value
    yield pack_stream(bytes)
    bytes[index] = prev_byte


def xor_string(data):
	return ''.join(chr(ord(char) ^ 0xFF) for char in data)


# Add random charcters
def add_random_characters():
    for i in range(num):
        randomChar = chr(random.randint(0, 0x20))
        randomPlace = random.randint(0, len(lines)-1)
        lines[lineNum] = lines[lineNum][:randomPlace] + randomChar + lines[lineNum][randomPlace:]    
    return lines


# Negate given numbers
def negate_number(lines):
    payload = ""
    for line in lines:
        try:
            temp = int(line[:-1])
        except ValueError:
            payload += line[:-1] + "\n"
        else:
            temp = str(-temp)
            payload += temp + "\n"
    return payload


# ADD THESE TO FUZZER 
'''
+ KEYWORDDS
+ CONTROL
+ NEGATE NUMBERS
+ CHANGE UP LOOPS
+ FIX CODECS
'''
def txt_fuzzer(binary_file, input_file):

    sample_txt = read_txt(input_file)
    perm_inputs = []

    # Generate cyclic payloads
    mutated_copy = copy.deepcopy(sample_txt)
    for chunk in cyclic_gen():
        mutated_copy.append(chunk)
        perm_inputs.append("".join(mutated_copy))
        #perm_inputs.append(chunk)

    # Generate format strings
    mutated_copy = copy.deepcopy(sample_txt)
    for fmtstring in format_strings():
        mutated_copy = copy.deepcopy(sample_txt)
        mutated_copy.append(fmtstring) 
        perm_inputs.append("".join(mutated_copy))
    

    # Expand line
    mutated_copy = copy.deepcopy(sample_txt)
    payload = ""
    for line in mutated_copy:
        payload += line[:-1] * 4 + "\n"
        perm_inputs.append("".join(payload))
    
    
    # Use known integers
    for num in KNOWN_INTS:
        mutation = copy.deepcopy(sample_txt)
        for line in range(len(mutation)):
            mutation = copy.deepcopy(sample_txt)
            mutation[line] = num + '\n'
            perm_inputs.append("".join(mutation))


    # Add large negatives
    for negative in large_negatives():
        mutation = copy.deepcopy(sample_txt)
        for line in range(len(mutation)):
            mutation = copy.deepcopy(sample_txt)
            mutation[line] = negative + '\n'
            perm_inputs.append("".join(mutation))


    # Add large positives
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
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

CYCLIC_PAYLOAD = [cyclic(100).decode(), cyclic(500).decode(), cyclic(1000).decode(), cyclic(5000).decode(), cyclic(10000).decode()]

SYSTEM_WORDS = [f'/bin/sh', f'/bin/bash', f'/bin/zsh', f'exit']


# read sameple file 
def read_txt(input_file):
    with open(input_file) as f:
        return f.readlines()

def large_negatives(sample_txt, perm_inputs):
    # Generate small numbers '32' for intruction size
    for i in range(0, 32):
        mutated_copy = copy.deepcopy(sample_txt)
        y = str(-(2 ** i))
        for line in range(len(mutated_copy)):
            mutated_copy = copy.deepcopy(sample_txt)
            mutated_copy[line] = y + '\n'
            perm_inputs.append("".join(mutated_copy))
    return perm_inputs

def large_positives(sample_txt, perm_inputs):
    # Generate large numbers '32' for intruction size
    mutated_copy = copy.deepcopy(sample_txt)
    for i in range(0, 32):
        y = str(2 ** i)
        for line in range(len(mutated_copy)):
            mutated_copy = copy.deepcopy(sample_txt)
            mutated_copy[line] = y + '\n'
            perm_inputs.append("".join(mutated_copy))
    return perm_inputs


# Format string fuzz technique
def format_strings(data='', offset=1):
    yield data + f'%{offset}$x'
    yield data + f'%{offset}$@'
    yield data + f'%{offset}$hn'
    yield data + f'%{offset}hhn'
    yield data + f'%{offset}$p'
    yield data + f'%{offset}$n'
    yield data + f'%{offset}$d'
    yield data + f'%{offset}$s'
    yield data + f'%99999$n'
    yield data + f'%400$n'
    for num in range(32):
        yield data + f'%{2**num}$n'


def generate_cyclic(sample_txt, perm_inputs):
    mutated_copy = copy.deepcopy(sample_txt)
    for chunk in CYCLIC_PAYLOAD:
        mutated_copy.append(chunk)
        perm_inputs.append("".join(mutated_copy))
    
    return perm_inputs

# Generate format
def generate_format_strings(sample_txt, perm_inputs):
    mutated_copy = copy.deepcopy(sample_txt)
    for fmtstring in format_strings():
        mutated_copy = copy.deepcopy(sample_txt)
        mutated_copy.append(fmtstring) 
        perm_inputs.append("".join(mutated_copy))
    return perm_inputs

# Byte flipping
def xor_bytes(input, index, mask):
    prev_byte = input[index]
    input[index] ^= mask
    yield ("".join(map(chr, input)))
    input[index] = prev_byte


# Xor-ing each character with 255
def str_xor(input):
    payload = ''
    for charc in input:
        payload = ''.join(chr(ord(charc) ^ 0xFF))
    return payload


def random_byte_flip(mutated_copy, perm_inputs):
    # bypass ^ error types convert to list of bytes
    input = list(("".join(mutated_copy)).encode())
    for index in range(len(input)):
            for i in range(len(BIT_FLIP_VALS)):
                mask = random.choice(BIT_FLIP_VALS)
                input[index] ^= mask
                perm_inputs.append("".join(map(chr, input)))
    return perm_inputs


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


def system_words(sample_txt, perm_inputs):
    for sysword in SYSTEM_WORDS: 
        mutated_copy = copy.deepcopy(sample_txt)
        mutated_copy.append(sysword)
        perm_inputs.append("".join(mutated_copy))
    return perm_inputs


def expand_line(sample_txt, perm_inputs):
    mutated_copy = copy.deepcopy(sample_txt)
    mc = ""
    for line in mutated_copy:
        mc += line[:-1] * 4 + "\n"
        perm_inputs.append("".join(mc))
    return perm_inputs


def xor_string(sample_txt, place, perm_inputs):
    mutated_copy = copy.deepcopy(sample_txt)
    for line in range(len(mutated_copy)):
        if place == 0:
            mutated_copy.insert(0, str_xor(mutated_copy[line]))
        elif place == 1:
            mutated_copy.append(str_xor(mutated_copy[line]))
        else:
            mutated_copy[line] = (str_xor(mutated_copy[line]) + '\n')
        perm_inputs.append("".join(mutated_copy))
    return perm_inputs





def txt_fuzzer(binary_file, input_file):

    sample_txt = read_txt(input_file)
    perm_inputs = []

    # Generate cyclic payloads
    perm_inputs = generate_cyclic(sample_txt, perm_inputs)

    perm_inputs = generate_format_strings(sample_txt, perm_inputs)
    
    # Append large_negatives
    perm_inputs = large_negatives(sample_txt, perm_inputs)

    # Append large positives
    perm_inputs = large_positives(sample_txt, perm_inputs)
 
    # # Append system words
    perm_inputs = system_words(sample_txt, perm_inputs)

    # # Expand line
    perm_inputs = expand_line(sample_txt, perm_inputs)


    # # Smartly negates all numbers in sample
    mutated_copy = copy.deepcopy(sample_txt)
    perm_inputs.append(negate_number(mutated_copy))

    # # Randomly flips bytes in sample
    mutated_copy = copy.deepcopy(sample_txt)
    perm_inputs = random_byte_flip(mutated_copy, perm_inputs)
    

    # xor-string with 255 and append
    perm_inputs = xor_string(sample_txt, 1, perm_inputs)
    
    # xor-string to the front of line
    perm_inputs = xor_string(sample_txt, 0, perm_inputs)
    

    # xor-string with newline
    perm_inputs = xor_string(sample_txt, 2, perm_inputs)

    # Use known integers
    for num in KNOWN_INTS:
        mutated_copy = copy.deepcopy(sample_txt)
        for line in range(len(mutated_copy)):
            mutated_copy = copy.deepcopy(sample_txt)
            mutated_copy[line] = num + '\n'
            perm_inputs.append("".join(mutated_copy))

    # XOR - bytes change input into bytes
    # from https://nitratine.net/blog/post/xor-python-byte-strings/
    mutated_copy = copy.deepcopy(sample_txt)
    list_of_bytes = list(("".join(mutated_copy)).encode())
    for line_no in range(len(list_of_bytes)):
        for mask in BIT_FLIP_VALS:
            for mutation in xor_bytes(list_of_bytes, line_no, mask):
                perm_inputs.append(mutation)

    return perm_inputs
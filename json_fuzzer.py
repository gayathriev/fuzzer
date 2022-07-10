from pwn import *
import sys
import os
import json
import copy
import random

def read_json(filename):
    f = open(filename)
    return json.load(f)


def mutate(json):
    res = copy.deepcopy(json)
    key = random.choice([res.keys()])
    for key in res.keys():
        if isinstance(res[key], int):
            res[key] = random.randint(-sys.maxsize, sys.maxsize)
        if isinstance(res[key], str):
            res[key] = mutate_string(res[key])
        if isinstance(res[key], list):
            index = random.randint(0, len(res[key]) - 1)
            if isinstance(res[key][index], int):
                res[key]  = random.randint(-sys.maxsize, sys.maxsize)
            if isinstance(res[key][index], str):
                res[key] = mutate_string(res[key][index])
    return res

def mutate_type(json):
    res = copy.deepcopy(json)
    for key in res.keys():
        type = random.randint(0, 7)
        if type == 0: # string
            res[key] = mutate_string('a'*random.randint(0, sys.maxsize))
        if type == 1: # int
            res[key] = random.randint(-sys.maxsize, sys.maxsize)
        if type == 2: # boolean
            res[key] = random.choice([True, False])
        if type == 3: # list TODO
            res[key] = list()
        if type == 4: # None
            res[key] = None
        if type == 5: # float
            res[key] = random.uniform(float('-inf'), float('inf'))
        if type == 6: # dict
            res[key] = res
    return res

        
    
################################
### STRING STUFF
################################
def mutate_string(string):
    size = random.randint(0, len(string) + 10)
    payload = ''
    payload = format_string(size)
    return payload

def format_string(size):
    identifiers = ['%c', '%x', '%d', '%p', '%s']
    identifier = random.choice(identifiers)
    payload = ''
    for i in range(size):
        payload += identifier + ' '
    return payload

#################################
###     TEST
#################################
def test_payload(binary_file, json):
    p = process('./' + binary_file)
    print(json)
    p.sendline(str(json).encode())
    mess = p.recvlines(2, timeout=0.1)
    print(mess)
    p.close()

#################################
###     MAIN STUFF
#################################
def json_fuzzer(binary_file, input, loops=10):
    json = read_json(input)
    for i in range(0, loops):
        try:
            test_payload(binary_file, json)
    
            res = mutate(json)
            test_payload(binary_file, res)
            
            res = mutate_type(json)
            test_payload(binary_file, res)
        except Exception as e:
            print(e)
    


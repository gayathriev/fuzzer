from pwn import *
import sys
import os
import json
import copy
import random

LOOPS = 100

def read_json(filename):
    f = open(filename)
    return json.load(f)


def mutate(json):
    res = copy.deepcopy(json)
    key = random.choice([res.keys()])
    random_numbers = generate_random_numbers(res['len'])
    for key in res.keys():
        if isinstance(res[key], int):
            res[key] = random.choice(random_numbers)
        if isinstance(res[key], str):
            res[key] = mutate_string(res[key])
        if isinstance(res[key], list):
            index = random.randint(0, len(res[key]) - 1)
            if isinstance(res[key][index], int):
                res[key]  = random.choice(generate_random_numbers(res[key][index]))
            if isinstance(res[key][index], str):
                res[key] = mutate_string(res[key][index]).upper()
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
            res[key] = {}
    return res

        
    
def generate_random_numbers(size = 100):
    nums = [0, 1, -1, -sys.maxsize, sys.maxsize, size, -size]
    for i in range(LOOPS):
        nums.append(random.randint(-size, size + 1000))
    return nums
################################
### STRING STUFF
################################
def mutate_string(string):
    size = random.randint(0, len(string) + 1000)
    payload = ''
    #payload = format_string(size)
    payload = get_random_string(size)
    return payload

def get_random_string(length):
    c = cyclic_gen()
    return c.get(length).decode()

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
def test_payload(binary_file, res):
    p = process('./' + binary_file)
    context.log_level = 'error'

    p.sendline(json.dumps(res).encode())
    p.proc.stdin.close()

    exit_status = None
    while exit_status == None:
        p.wait()
        exit_status = p.returncode
    print("exit status:", exit_status, "-- segfault" if exit_status == -11 else '')

    mess = p.recvline(timeout = 0.1)
    print('len: ', res['len'], 'input len: ', len(res['input']), mess)
    p.close()

#################################
###     MAIN STUFF
#################################
def json_fuzzer(binary_file, input, loops=100):
    json = read_json(input)
    test_payload(binary_file, json)

    for i in range(0, LOOPS):
        try:
            res = mutate(json)
            print('===', res['len'], '===', len(res['input']))
            test_payload(binary_file, res)
            
            res = mutate_type(json)
            print('===', res['len'], '===', len(res['input']))
            test_payload(binary_file, res)
        except Exception as e:
            print(e)
    
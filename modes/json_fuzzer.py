from pwn import *
import sys
import os
import json
import copy
import random
from support.log_crash import log_crash_json
from Harness import Harness
import coverage

LOOPS = 6000

def read_json(filename):
    f = open(filename)
    return json.load(f)


def mutate(js):
    res = copy.deepcopy(js)
    key = random.choice(list(res.keys()))

    for key in res.keys():
        if isinstance(res[key], int):
            random_numbers = generate_random_numbers(res[key])
            res[key] = random.choice(random_numbers)
        elif isinstance(res[key], str):
            res[key] = mutate_string(res[key])
        elif isinstance(res[key], list):
            if len(res[key]) == 0:
                res[key].append(random.randint(0, 0xfffff))
            else:
                index = random.randint(0, (len(res[key]) - 1))
                if isinstance(res[key][index], int):
                    res[key] = generate_random_numbers(res[key][index])
                if isinstance(res[key][index], str):
                    res[key][index] = mutate_string(res[key][index]).upper()
    return res

def nullify(js):
    res = copy.deepcopy(js)
    for key in res.keys():
        if isinstance(res[key], int):
            res[key] = 0
        elif isinstance(res[key], list):
            res[key] = []
        elif isinstance(res[key], str):
            res[key] = ""
        else:
            res[key] = None
    return res

def mutate_type(js):
    res = copy.deepcopy(js)
    for key in res.keys():
        type = random.randint(0, 7)
        if type == 0: # string
            res[key] = mutate_string('a'*random.randint(0, 0xffff))
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
        try:
            nums.append(random.randint((size - 1000), (size + 1000)))
        except Exception as e:
            print(size)
            print(e)
    return nums

################################
### STRING STUFF
################################
def mutate_string(string):
    size = random.randint(0, (len(string) + 1000))
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
def test_payload(harness, binary_file, res):

    payload = json.dumps(res)
    exit_status = harness.start_process(payload.encode())

    if (exit_status == -11):
        print("Program terminated: Check 'bad.txt' for output")
        log_crash_json(res)
        exit(0)
    elif (exit_status != 0):
        print("Program terminated: Check 'bad.txt' for output")
        print("status code: ", exit_status)
        log_crash_json(res)
        exit(0)


#################################
###     MAIN STUFF
#################################
def json_fuzzer(harness, binary_file, input, loops=LOOPS):
    js = read_json(input)
    print("============== running json fuzzer ==============")
    test_payload(harness, binary_file, js)
    res = nullify(js)
    test_payload(harness, binary_file, res)
    entropy = res
    for i in range(0, LOOPS):
        try:
            res = mutate(js)
            test_payload(harness, binary_file, res)
            
            res = mutate_type(js)
            test_payload(harness, binary_file, res)


            entropy = mutate(entropy)
            test_payload(harness, binary_file, entropy)

            entropy = mutate_type(entropy)
            test_payload(harness, binary_file, entropy)
                   
        except Exception as e:
            print("exception", e)


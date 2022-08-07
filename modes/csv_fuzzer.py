from pwn import *
import csv
from enum import Enum
import random
import math
from support.log_crash import log_crash
class Payload(Enum):
    EMPTY = 1
    INVALID = 2
    OVERFLOW_LINE = 3
    OVERFLOW_ENTRY = 4
    DELIMITER = 5
    FORMAT_STRING = 6
    BYTE_FLIP = 7
    NUM_ZERO = 8
    NUM_NEGATIVE = 9
    NUM_LARGE = 10
    NUM_FLOAT = 11 


"""
    
    Process & Payload Handlers
    ----------------------------------
    These processes will parse our sample payload, handle communication to the process to test, and test our payloads.
"""

# Given the argument p, will attempt to open up the process.
def open_process_csv(p):
    try:
        return process('./' + p,stdin=PTY,raw=False)
    except Exception as e:
        print("invalid binary :(")
        print(e)
        sys.exit() 

# Given the argument path, will attempt to parse the data into a 2d array
def parse_csv_input(path):

    data = []
    try:
        print("this is a list?")
        print(path)
        with open(path, newline='') as csv_file:
            print(csv_file)
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                print(len(row))
                data.append(row)
    except Exception as e:
        print("invalid data :(")
        print(e)
        sys.exit() 
    print("this is the data extracted:")
    print(data)
    return data

# Given a processed csv 2d array, will grab the header i.e. the first line and return it.
def generate_header(data):
    payload = b''
    for entry in data[0]:
        payload += bytes(entry,'utf-8')
        payload += b','

    payload = payload[:-1]
    payload += b'\n'

    return payload


"""
    Payload Generators
    ----------------------------------
    Will generate payloads of specific types and structure given the structre of the sample payload, and then pass the generated payload to test_payload() to test.

    All payload generators take in the following arguments:

    process - the process to test
    data - the data from the sample payload
    send_header - a boolean that if set to True, will keep the header intact for the payload.
"""

##
##  empty_payload() generates a payload with only delimiters and no data
##

def empty_payload(process, data, send_header):
    delimiter = len(data[0])
    if(delimiter < 0):
        delimiter = 0

    payload = b''

    if(send_header == True):
        payload = generate_header(data)
    

    payload += ((b','*(delimiter-1)) + b'\n')

    #return test_payload(process,payload)
    return payload

##
##  zero_payload() generates a payload with all data entries set to zero.
##
def zero_payload(process, data, send_header):
    delimiter = len(data[0])
    if(delimiter < 0):
        delimiter = 0

    payload = b''

    if(send_header == True):
        payload = generate_header(data)

    string = b'0,' * delimiter
    string = string[:-1]
    string += b'\n'
    string *= len(data)

    payload += string
    
    return payload

##
##  empty_payload() generates a payload with only delimiters and no data
##
def format_payload(process, data, send_header):
    delimiter = len(data[0])
    if(delimiter < 0):
        delimiter = 0

    payload = b''

    if(send_header == True):
        payload = generate_header(data)


    string = b'%x,' * delimiter
    string = string[:-1]
    string += b'\n'

    payload += string

    string = b'%s,' * delimiter
    string = string[:-1]
    string += b'\n'

    payload += string
    
    return payload


def max_payload(process, data, send_header):
    delimiter = len(data[0])
    if(delimiter < 0):
        delimiter = 0

    payload = b''

    if(send_header == True):
        payload = generate_header(data)

    string = ''

    for i in range(0,len(data[0])):
        string += (str(random.randrange((2 **63),(2 ** 64))) + ',') * delimiter
        string = string[:-1]
        string += str(b'\n','utf-8')

    payload += bytes(string,'utf-8')
    
    return payload

def long_payload(process, data, send_header):
    delimiter = len(data[0])
    if(delimiter < 0):
        delimiter = 0

    payload = b''

    if(send_header == True):
        payload = generate_header(data)

    string = ''

    for i in range(0,len(data[0])):
        string += (str(random.randrange((2 **63),(2 ** 64))) + ',') * delimiter
        string = string[:-1]
        string += str(b'\n','utf-8')

    payload += bytes(string,'utf-8')

    payload *= 5000
    
    return payload

##
##  negative_payload() generates a payload with all data entries set to negative one.
##
def negative_payload(process, data, send_header):
    delimiter = len(data[0])
    if(delimiter < 0):
        delimiter = 0

    payload = b''

    if(send_header == True):
        payload = generate_header(data)

    string = ''
    for i in range(0,len(data)):
        for j in range(0,len(data[0])):
            string += (str(random.randrange(-(2 **32),0)) + ',')
        string = string[:-1]
        string += str(b'\n','utf-8')

    payload += bytes(string,'utf-8')

    print(payload)
    
    return payload
    
##
##  large_payload() generates a payload with large data for each csv entry, with size specified with the size parameter.
##
def large_payload(process, data, size, send_header):
    delimiter = len(data[0])
    if(delimiter < 0):
        delimiter = 0

    header = ''
    if(send_header == True):
        header = generate_header(data)

    string = b'a'*size + b','
    string *= delimiter
    string = string[:-1]
    string += b'\n'
    string *= len(data)

    if(send_header == True):
        payload = header + string
        return payload
    else:
        return string

def float_payload(process, data, send_header):
    delimiter = len(data[0])
    if(delimiter < 0):
        delimiter = 0

    payload = b''

    if(send_header == True):
        payload = generate_header(data)

    string = ''

    for i in range(0,len(data[0])):
        string += (str(random.random()) + ',') * delimiter
        string = string[:-1]
        string += str(b'\n','utf-8')

    payload += bytes(string,'utf-8')
    
    print(payload)

    return payload


def flip_payload(process, data, send_header):
    delimiter = len(data[0])
    if(delimiter < 0):
        delimiter = 0

    header = ''
    for i in range(0,len(data[0])):
        header += data[0][i] + ','

    header = header[:-1]
    header += str(b'\n','utf-8')

    string = ''

    for i in range(0,len(data)):
        for j in range(0,len(data[i])):
            string += data[i][j] + ','
        string = string[:-1]
        string += str(b'\n','utf-8')


    arr = bytearray(string,'utf-8')
    arr *= 5
    print(string)
    print(arr)
    for i in range(0,len(arr)):
        if chr(arr[i]) == ',' or chr(arr[i]) == '\n':
            continue;
        else:
            if(random.randint(0,5) == 0):
                arr[i] ^= random.getrandbits(8)
    
    if(send_header == True):
        payload = bytearray(header,'utf-8') + arr
        print(payload)
        return payload
    else:
        return arr

"""

    Test code for payloads, will print out reports in the console

"""

def csv_fuzzer(process,file):
    data = parse_csv_input(file)

    payloads = []

    payloads.append(empty_payload(process,data,True))
    payloads.append(empty_payload(process,data,False))

    payloads.append(zero_payload(process,data,True))
    payloads.append(zero_payload(process,data,False))

    payloads.append(negative_payload(process,data,True))
    payloads.append(negative_payload(process,data,False))

    payloads.append(large_payload(process,data,100,True))
    payloads.append(large_payload(process,data,100,False))

    payloads.append(max_payload(process,data,True))
    payloads.append(max_payload(process,data,False))

    payloads.append(float_payload(process,data,True))
    payloads.append(float_payload(process,data,False))

    payloads.append(flip_payload(process,data,True))
    payloads.append(flip_payload(process,data,False))

    payloads.append(long_payload(process, data, True))
    payloads.append(long_payload(process, data, False))

    payloads.append(format_payload(process, data, True))
    payloads.append(format_payload(process, data, False))

    return payloads
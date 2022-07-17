from pwn import *
import csv
from enum import Enum

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
        return process('./' + p)
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

# Given a payload, will send it to the program 5000 times, returning a negative number if the program hasn't crashed within this time. Otherwise, it will return the amount of times the payload needs to be inputted to crash the program.
def test_payload(process, payload):

    p = open_process_csv(process)

    run = 0

    while run <= 5000:
        try:
            p.sendline(payload)
            run+=1
        except:
            p.wait_for_close()
            return_tuple = (run, p.returncode)
            return return_tuple
            break;

    return_tuple = (run * -1, p.returncode)
    return return_tuple

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
    

    payload += ((b','*delimiter) + b'\n')*len(data)
    payload = payload[:-1]

    return test_payload(process,payload)

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
    
    return test_payload(process,payload)

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

    string = b'-1,' * delimiter
    string = string[:-1]
    string += b'\n'
    string *= len(data)


    payload += string
    payload = payload[:-1]
    
    return test_payload(process,payload)
    
##
##  large_payload() generates a payload with large data for each csv entry, with size specified with the size parameter.
##
def large_payload(process, data, size, send_header):
    delimiter = len(data[0])
    if(delimiter < 0):
        delimiter = 0

    string = b'a'*size + b','
    string *= delimiter
    string = string[:-1]
    string += b'\n'
    string *= len(data)
    string = string[:-1]

    return test_payload(process,string)


"""

    Test code for payloads, will print out reports in the console

"""

def csv_payload(process,data):
    data = parse_csv_input(sys.argv[2])

    runs = empty_payload(sys.argv[1],data,True)
    print("runs required for empty payload: " + str(runs[0]))
    print("return code for this run was: " + str(runs[1]))

    runs = zero_payload(sys.argv[1],data,True)
    print("runs required for zero payload: " + str(runs[0]))
    print("return code for this run was: " + str(runs[1]))

    runs = negative_payload(sys.argv[1],data,True)
    print("runs required for negative payload: " + str(runs[0]))
    print("return code for this run was: " + str(runs[1]))

    runs = large_payload(sys.argv[1],data,100,True)
    print("runs required for large payload: " + str(runs[0]))
    print("return code for this run was: " + str(runs[1]))




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

def run_test(process,payload,multiplier):
    p = open_process_csv(process)

    for i in range(0,multiplier):
        p.send(payload)

    p.send(b'\4')

    p.wait_for_close(timeout=0.5)

    return p.poll()


# Given a payload, will send it to the program 5000 times, returning a negative number if the program hasn't crashed within this time. Otherwise, it will return the amount of times the payload needs to be inputted to crash the program.
def test_payload(process, payload):
    
    
    run = 0
    bad = b''

    l = 1
    r = 5000

    while(l <= r):
        results = (run_test(process,payload,l),run_test(process,payload,r))

        #print(results)

        m = math.floor((l+r)/2)

        if(results[0] != -11 and results[1] == -11):
            #print("values of l and are are: " +str(l) + " " + str(r))
            #print("value of m is " + str(m))
            if(run_test(process,payload,m) == -11):
                r = m - 1
            else:
                l = m + 1
            #print("values of l and are are: " +str(l) + " " + str(r))
        elif(results[0] != -11 and results[1] != -11):
            #print("values of l and are are: " +str(l) + " " + str(r))
            #print("failure")
            return_tuple = (5000 * -1, results[1])
            return return_tuple
        else:
            #print("values of l and are are: " +str(l) + " " + str(r))
            #print(results)
            #print('badtext')
            if(results[0] == -11):
                run = l
            else:
                run = r
            break;

    bad = payload * run
    
    #p.send(b'\x04')
    #print("run is: " + str(run))
    bad = bad[:-1]

    print("Program terminated: Check 'bad.txt' for output")
    log_crash(str(bad,'utf-8'))
    exit(0)

    #return_tuple = (run * -1, p.returncode)
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
    
    #payload = payload[:-1]
    #return test_payload(process,payload)
    return payload


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
    
    #payload = payload[:-1]
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
    
    #return test_payload(process,payload)
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
    
    #return test_payload(process,payload)
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
    
    #return test_payload(process,payload)
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
        #return test_payload(process,payload)
        return payload
    else:
        #return test_payload(process,string)
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

    #return test_payload(process,payload)
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
    #print(arr)
    
    if(send_header == True):
        payload = bytearray(header,'utf-8') + arr
        print(payload)
        #return test_payload(process,bytes(payload))
        return payload
    else:
        #return test_payload(process,bytes(arr))
        return arr

"""

    Test code for payloads, will print out reports in the console

"""

def csv_fuzzer(process,file):
    data = parse_csv_input(file)

    payloads = []

    #runs.append(blank_payload(process, data, True))
    #runs.append(blank_payload(process, data, False))

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

    #print(payloads)

    return payloads
    """print("--------------------------------------------")
    print("runs required for empty payload: " + str(runs[0][0]))
    print("return code for this run was: " + str(runs[0][1]))

    print("\nruns required for empty payload (without header): " + str(runs[1][0]))
    print("return code for this run was: " + str(runs[1][1]))
    print("--------------------------------------------")

    print("--------------------------------------------")
    print("runs required for zero payload: " + str(runs[2][0]))
    print("return code for this run was: " + str(runs[2][1]))

    print("\nruns required for zero payload (without header): " + str(runs[3][0]))
    print("return code for this run was: " + str(runs[3][1]))
    print("--------------------------------------------")
    
    print("--------------------------------------------")
    print("runs required for negative payload: " + str(runs[4][0]))
    print("return code for this run was: " + str(runs[4][1]))

    print("\nruns required for negative payload (without header): " + str(runs[5][0]))
    print("return code for this run was: " + str(runs[5][1]))
    print("--------------------------------------------")
    
    print("--------------------------------------------")
    print("runs required for large payload: " + str(runs[6][0]))
    print("return code for this run was: " + str(runs[6][1]))

    print("\nruns required for large payload (without header): " + str(runs[7][0]))
    print("return code for this run was: " + str(runs[7][1]))
    print("--------------------------------------------")

    print("--------------------------------------------")
    print("runs required for max payload: " + str(runs[8][0]))
    print("return code for this run was: " + str(runs[8][1]))

    print("\nruns required for max payload: " + str(runs[9][0]))
    print("return code for this run was: " + str(runs[9][1]))
    print("--------------------------------------------")

    print("--------------------------------------------")
    print("runs required for float payload: " + str(runs[10][0]))
    print("return code for this run was: " + str(runs[10][1]))

    print("\nruns required for float payload (without header): " + str(runs[11][0]))
    print("return code for this run was: " + str(runs[11][1]))
    print("--------------------------------------------")

    print("--------------------------------------------")
    print("runs required for flip payload: " + str(runs[12][0]))
    print("return code for this run was: " + str(runs[12][1]))

    print("\nruns required for flip payload (without header): " + str(runs[13][0]))
    print("return code for this run was: " + str(runs[13][1]))
    print("--------------------------------------------")"""



#csv_payload('./csv2','csv2.txt')


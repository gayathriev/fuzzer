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

# 
#   Open process, process location is a string
#
def open_process_csv(p):
    try:
        return process('./' + p)
    except Exception as e:
        print("invalid binary :(")
        print(e)
        sys.exit() 

# 
#   Open process, data location is a string
#
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

# send the header of the csv file as one line.
def send_header(process,data):
    payload = ""
    for entry in data[0]:
        payload += entry
        payload += ','
    return payload

def generate_header(process,data):
    payload = b''
    for entry in data[0]:
        payload += bytes(entry,'utf-8')
        payload += b','

    payload = payload[:-1]
    payload += b'\n'

    return payload

def empty_payload(process, data, send_header):
    delimiter = len(data[0])
    if(delimiter < 0):
        delimiter = 0

    print("delimiter is " + str(delimiter))
    i = 0

    payload = b''

    if(send_header == True):
        payload = generate_header(process,data)
    

    payload += ((b','*delimiter) + b'\n')*len(data)

    while 1==1:
        process.sendline(payload)
        i+=1
        print(i)

def zero_payload(process, data, send_header):
    delimiter = len(data[0])
    if(delimiter < 0):
        delimiter = 0

    print("delimiter is " + str(delimiter))
    i = 0

    payload = b''

    if(send_header == True):
        payload = generate_header(process,data)



    string = b'0,' * delimiter
    string = string[:-1]
    string += b'\n'
    string *= len(data)

    payload += string

    while 1==1:

        process.sendline(payload[:-1])
        i+=1
        print(i)

def negative_payload(process, data, send_header):
    delimiter = len(data[0])
    if(delimiter < 0):
        delimiter = 0

    print("delimiter is " + str(delimiter))
    i = 0

    payload = b''

    if(send_header == True):
        payload = generate_header(process,data)

    string = b'-1,' * delimiter
    string = string[:-1]
    string += b'\n'
    string *= len(data)


    payload += string

    while 1==1:

        process.sendline(payload)
        i+=1
        print(i)


def large_payload(process, data, size, send_header):
    delimiter = len(data[0])
    if(delimiter < 0):
        delimiter = 0

    print("delimiter is " + str(delimiter))
    i = 0

    string = b'a'*size + b','
    string *= delimiter
    string = string[:-1]

    while 1==1:

        process.sendline(string)
        i+=1
        print(i)



#TODO: add detection of when the program is just running and not resolving

# Program will take in two arguments
p = open_process_csv(sys.argv[1])
data = parse_csv_input(sys.argv[2])

zero_payload(p,data,True)
p.interactive()

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


def open_process_csv():
    try:
        p = process("./" + sys.argv[1])
        context.log_level = 'debug'
        return p
    except Exception as e:
        print("invalid binary :(")
        print(e)
        sys.exit() 

def parse_csv_input():

    data = []

    try:
        print(sys.argv[2])
        with open(sys.argv[2], newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                print(len(row))
                data.append(row)
    except Exception as e:
        print("invalid csv input :^(")
        print(e)
        sys.exit() 

    return data

"""gdb.attach('image-viewer','''
set follow-fork-mode child
break execve
continue
''')"""

def empty_payload(process, data):
    delimiter = len(data)-2
    if(delimiter < 0):
        delimiter = 0

    print("delimiter is " + str(delimiter))
    i = 0

    while 1==1:
        process.sendline(b','*delimiter)
        i+=1
        print(i)

def zero_payload(process, data):
    delimiter = len(data)-1
    if(delimiter < 0):
        delimiter = 0

    print("delimiter is " + str(delimiter))
    i = 0

    string = b'0,' * delimiter
    string = string[:-1]

    while 1==1:

        process.sendline(string)
        i+=1
        print(i)

def negative_payload(process, data):
    delimiter = len(data)-1
    if(delimiter < 0):
        delimiter = 0

    print("delimiter is " + str(delimiter))
    i = 0

    string = b'-1,' * delimiter
    string = string[:-1]

    while 1==1:

        process.sendline(string)
        i+=1
        print(i)

#TODO: add detection of when the program is just running and not resolving

p = open_process_csv()
data = parse_csv_input()
print(data)

p.interactive()

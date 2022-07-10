from pwn import *
import csv

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

p = open_process_csv()
data = parse_csv_input()

print(data)

p.interactive()

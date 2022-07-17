'''

Simple module writes the bad input to a file

'''

def log_crash(crash_input):
    str_input = str(crash_input)
    with open('./bad.txt', 'w') as crash:
        crash.write(str_input)
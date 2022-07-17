'''

Simple module writes the bad input to a file

'''

def log_crash(crash_input):
    crash_message = "CRASH FOUND: "
    str_input = str(crash_input)
    crash_message += str_input
    crash_message += '\n'
    with open('./crash.txt', 'w') as crash:
        crash.write(crash_message)
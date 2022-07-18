import json
'''

Simple module writes the bad input to a file

'''

def log_crash(crash_input):
    str_input = str(crash_input)
    str_input += '\n'
    with open('./bad.txt', 'w') as crash:
        crash.write(str_input)

def log_crash_json(crash_input):
    str_input = str(crash_input)
    str_input += '\n'
    with open('./bad.txt', 'w') as crash:
        crash.write(json.dumps(crash_input))

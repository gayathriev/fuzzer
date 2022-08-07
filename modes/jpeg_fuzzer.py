from pwn import *
from PIL import Image, ImageChops
import sys
import os
import copy
import random
import itertools
#from support.log_crash import log_crash_jpeg
 
LOOPS = 100

# This fuzzer will attempt to use direct manipulation of input JPEG data
# as well as manipulation via the PIL library

def read_jpeg(filename):
    jpeg = Image.open(filename)
    return jpeg

def mutate_type(jpeg):
    res = copy.deepcopy(jpeg)
    for key in res.keys():
        type = random.randint(0, 7)
        if type == 0: # Mutate file size/scale
            res[key] = scale_change(jpeg)
        if type == 1: # invert file values
            res[key] = invert_values(jpeg)
        if type == 2: # insert special bytes
            res[key] = insert_special_bytes(jpeg)
        if type == 3: # Use the 64 bit method
            pass
            #res[key] = b64_fuzz(jpeg)
        if type == 4: # flip random bits
            res[key] = bit_flip(jpeg)
        if type == 5: # float
            res[key] = random.uniform(float('-inf'), float('inf'))
        if type == 6: # dict
            res[key] = {}
    return res


# Attempt to mutate the sample input 
# NOTE: the first 4 characters of the file must be maintained to ensure that it remains a valid 
# JPEG file - these characters are: FF D8
 
#Change the scale of the input image randomly amongst set size values
def scale_change(jpeg):
    scales_list = [1, 16, 64, 256, 4096, 65535, 65536]
    x = random.sample(scales_list, 1) 
    y = random.sample(scales_list, 1)
    res = jpeg.resize((x, y))
    return res

def bit_flip(jpeg):
    num_of_flips = int((len(jpeg) - 4) * 0.0001)
    indexes = range(0x550, len(jpeg) - 4)

    chosen_indexes = []

    #TODO iterate indexes until we've flipped the determined number
    for i in range(0, num_of_flips):
        chosen_indexes.append(random.choice(indexes))
    #TODO change this ------- bytearray versin
    new_img = jpeg[:]
    chosen_indexes = chosen_indexes[:1]
    for x in chosen_indexes:
        if (0xFF in jpeg[x-10:x+10]):
            continue
        current = jpeg[x]
        target = random.choice(range(0,8))
        mask = 0b1 << target
        new_img[x] = current ^ mask

    return bytes(new_img)

#Function that simply inverts the values of the JPEG file
def invert_values(jpeg):
    res = ImageChops.invert(jpeg)
    return res

#Function that randomly inserts special JPEG characters into a target JPEG file
def insert_special_bytes(jpeg):
        jpeg_data = data[:]

        special_bytes = [
			[0x00], [0xFF], [0x7F], [0xFF, 0xFF], [0x00, 0x00], 
            [0x00, 0x00, 0x00, 0x00], [0x40, 0x00, 0x00, 0x00], 
			[0x80, 0x00, 0x00, 0x00], [0x7F, 0xFF, 0xFF, 0xFF],
            [0xFF, 0xFF, 0xFF, 0xFF], [0xD8], [0xD9],
            [0xFF, 0xD8], [0xFF, 0xD9]
		]

        #choose special byte lists and generate a resultant list of the selection
        if (i == None):
            res_list = random.choice(special_bytes)
        else:
            res_list = special_bytes[i]
        
        #limit permutations to the region between the first and last 50 bytes of information
        i = 50
        while(0xFF in data[i-50:i+50]):
            i = random.choice(range(50, len(data) - 50))

        #choose elements 'e', of the resultant list and insert at location 'i'
        count = 0
        for e in res_list:
            jpeg_data[i + count] = e
            count += 1
        return bytes(jpeg_data)

# def mutate(jpeg):
#     res = copy.deepcopy(jpeg)
#     key = random.choice([res.keys()])
#     random_numbers = generate_random_numbers(res['len'])
#     for key in res.keys():
#         if isinstance(res[key], int):
#             res[key] = random.choice(random_numbers)
#         if isinstance(res[key], str):
#             res[key] = mutate_string(res[key])
#         if isinstance(res[key], list):
#             index = random.randint(0, len(res[key]) - 1)
#             if isinstance(res[key][index], int):
#                 res[key]  = random.choice(generate_random_numbers(res[key][index]))
#             if isinstance(res[key][index], str):
#                 res[key] = mutate_string(res[key][index]).upper()
#     return res

# def b64_fuzz(jpeg):
# 	keys = []
# 	values = []
# 	for key, value in jpeg.info.items():
# 		keys.append(key)
# 		values.append(value)
# 	# key value initialisation
# 	for i in range(len(keys)):
# 		for j in range(10):
# 			jpeg.info.__setitem__(keys[i]*j, values[i]*j*2)
# 			payloads.append(jpeg)

# 	# Using b64 method
# 	with open(testInput, "rb") as f:
# 		b64str = base64.b64encode(f.read())
# 	i = 0
# 	for c in str(b64str):
# 		if c == '/':
# 			# generate random 8 byte hex number and insert
# 			# after every slash
# 			rpt = binascii.b2a_hex(os.urandom(8))
# 			payload = b64str[:i] + rpt + b64str[i:]
# 			# Assert b64 string is 4 byte aligned
# 			if(len(payload) % 4 != 0):
# 				payload += b'='
# 			payload = base64.b64decode(b"data:image/jpeg;base64," + payload)
# 			payloads.append(payload)
# 		i += 1

def test_payload(binary_file, jpeg):
    p = process('./' + binary_file)
    payload = jpeg
    p.send(payload)
    p.proc.stdin.close()

    exit_status = None
    while exit_status == None:
        p.wait()
        exit_status = p.returncode
    if (exit_status == -11):
        print("Program terminated: Check 'bad.txt' for output")
        log_crash(payload.decode("utf-8"))
        exit(0)

#################################
###     MAIN
#################################
def jpeg_fuzzer(binary_file, input):
    jpeg = read_jpeg(input)
    #test_payload(binary_file, jpeg)
    print("============== running jpeg fuzzer ==============")
    for i in range(0, LOOPS):
        try:
            #res = mutate(jpeg)
            # print('===', res['len'], '===', len(res['input']))
            #test_payload(binary_file, res)
            
            yield mutate_type(jpeg)
            # print('===', res['len'], '===', len(res['input']))
            #test_payload(binary_file, res)
        except Exception as e:
            pass
            #print(e)
    
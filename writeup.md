Midpoint Writeup 

The current iteration of the fuzzer can be most easily described as a basic assembly of 
modules, each of which are selected for use following the identification of the file type 
of a sample file – presently it is capable of identification of the following types: 
CSV, ELF, JPEG, JSON, PDF, and XML. This was done through the implementation of the 
detect.py module, which uses a plethora of Python libraries to determine the file type 
based on features of the stated types, otherwise it will attempt to handle the file as 
plain text. On discovery of the type, the corresponding fuzzer module will be selected and 
executed as a subprocess that runs until an exploitable error occurs, the input and error 
message for which is then stored in a text file for further examination; execution is then 
halted. 

As the fuzzer exists in its present form, it is capable of successfully causing and 
detecting errors in CSV, JSON and XML binaries, however, functionality of the ELF, JPEG,
Plain Text, and PDF will be added in future versions. 

CSV Module Functionality:
The CSV module, csv_fuzzer.py takes in a sample input such as csv1.txt, which serves as
the structure for the generated payloads. The generated payloads cover several general
cases where, the payload is all zeroes, the payload is all negative numbers, the payload
is empty but contains correct delimiters, and the case where the payload has large values.
Each of these payloads are sent to the binary and a resultant tuple is generated,
containing the corresponding return code, and the number of times the payload was given
as input. 

JSON Module Functionality 
The JSON module, json_fuzzer.py takes a sample input, such as json1.txt, mutates the input
data by maintaining the data types, such as mutating MAXINT to +MAXINT but maintaining the
integer type. Inversely, some mutated input changes the data type, such as converting a
Boolean value to an integer field. These payloads are sent to the binary, and which waits
for a return code, such as -11 (SIGSEGV) or 0 which indicates normal function. 

XML Module Functionality
The XML module, xml_fuzzer.py takes a sample XML such as xml1.txt, as input and mutates it
to fuzz exploits from a given binary. It can currently mutate the input in the following
ways – spawn child nodes to a single parent at random times for breadth, and recursively
add child nodes at random times for depth, it is also capable of injecting large strings
to links to potentially cause buffer overflow and inject format strings to links to cause
data leaks. 

As with the unimplemented types, the harness functionality is yet to be fully implemented.
Once implemented, it will be used to make the fuzzer function as a cohesive system capable
of producing subprocesses which can reliably fuzz a target binary, given a sample input
file. 
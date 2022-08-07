 =================================== __FUZZER WRITEUP__ =======================================
HOW TO RUN
Please note that this current version runs using the following commands and
dependencies:
```
sudo apt-get install python3-magic
sudo apt-get install python3-pillow
Python3 fuzzer [target binary] [sample file.txt] 
```
===================================     __USAGE__     ====================================

`./fuzzer <target binary> <sample input>`

The current input types supported are:
* CSV
* PDF
* JPEG
* JSON
* TXT
* XML

=================================  __DESIGN OVERVIEW__  ==================================

*********************
This fuzzer iteration is capable of detecting CSV, ELF, JPEG, JSON, PDF and XML input
modules, each of which are selected for use following
This iteration of the fuzzer is capable of the identification of the file type of a sample
file – presently being capable of identifying any of the following types: CSV, ELF, JPEG,
JSON, PDF, and XML. This was done through the implementation of the detect.py module, 
which uses a plethora of Python libraries to determine the file type based on features of 
the stated types, otherwise it will attempt to handle the file as plain text. On discovery
of the type, the corresponding fuzzer module will be selected and executed as a subprocess
that runs until an exploitable error occurs, the input for which will be stored in a text 
file titled bad.txt for further examination. Currently it is capable of successfully 
handling, CSV, JSON, TXT, and XML, with some functionality for the detection and fuzzing
of binaries which take PDF and JPEG as input. 

The software was designed with the following components which work both independently and 
together to provide the fuzzer with the desired capabilities.

* Initialisation script
* Harness
* Methods
* Support

The harness and support modules are interdependent systems which each work to allow the
highly modular methods system to work in a congruent fashion. 

__Harness__
In the most fundamental sense, the purpose of the harness is to handle and direct the 
input of data in the form of an executable binary and sample input file. It also works to
detect and handle crashes, hangs, and infinite loops of subprocesses. The binary file is 
used by the harness to launch a subprocess of the target program, whilst the sample file 
is used to select a fuzzer module in order to generate input permutations and strategies 
to try against the subprocess for fuzzing. 

__Support__
If the harness system is the brain of the fuzzer, the support system would be the nervous
system that tells the body how to react to input. The support system can correctly 
identify the format type of an input sample file of a '.txt' format via the detect.py 
module. This is done by using unique aspects of the CSV, PDF, TXT, JPEG, JSON and XML file
types, thereby giving the harness the ability to select the correct fuzzer for input 
generation. 
The support system is perhaps the most important aspect of the entire fuzzer due to the 
'log_crash.py' and 'generate_summary.py' modules. The summary and crash log features grant 
the user the ability to visualise key analytics and information pertaining to the supplied
binary, following successful exploitation.

This include information on:
* number of hangs
* number of aborts
* overall code-coverage
* time-elapsed 
* register values at time of crash
* input of interest

Once a crash occurs, the harness will log the error code produced by the failed process, 
parse this as crash_input to the support system and save it as a 'bad.txt' file. A core
file is also produced and with the use of the Pwntools library, ELF symbols are extracted
to give the exact values of the registers (EAX, EIP, ESP etc) and key memory addresses,
that are then directed to stdout. 

__CSV Module__
On selection, the CSV fuzzer will produce mutated output using the sample input as a basis
of the payload structure. In general, this method covers the following cases:

* Zeroes 
* Very large negative numbers
* Very large positive numbers
* Empty with correct delimiters
* Large amounts of input
* Flipped bits
* Format strings

The CSV module, csv_fuzzer.py takes in a sample input such as csv1.txt, which serves as
the structure for the generated payloads. The generated payloads cover several general
cases where, the payload is all zeroes, the payload is all negative numbers, the payload
is empty but contains correct delimiters, the payload contains fomrat strings, the payload
contains a large amount of input, and the payload has random bits flipped. The module also
tests payloads with and without a header.

On selection, the CSV fuzzer will produce mutated output using the sample input as a basis
of the payload structure. In general, this method covers the following cases:
* Zeroes 
* Very small negative numbers
* Very large positive numbers
* Empty with correct delimiters
* Large values
* Flipped bits
* ASCII bytes

The CSV module, csv_fuzzer.py takes in a sample input such as csv1.txt, which serves as
the structure for the generated payloads. The generated payloads cover several general
cases where, the payload is all zeroes, the payload is all negative numbers, the payload
is empty but contains correct delimiters, and the case where the payload has large values.
Each of these payloads are sent to the binary and a resultant tuple is generated,
containing the corresponding return code, and the number of times the payload was given
as input.
 
__PDF Module__
Following selection of the PDF module by the harness module, the PDF module will attempt
to fuzz the target binary with use of the PyPDF2 library, which allows for the
implementation of several strategies of varying effectiveness. 
The primary targets of this fuzzer are the filter and parser systems present in binaries
which handle PDF files. This is done by replacing the compression filter type to any of
the following: FlatDecode, ASCIIHexDecode, ASCII85Decode, LZWDecode, RunLengthDecode,
CCITTFax, JBIG2Decode, DCTDecode, JPXDecode, and Crypt. Once this is attempted, the fuzzer
will then attempt format(x) string injections in conjunction with very large inputs 
(>2000 pages), to cause a buffer overflow or data leak. 
This large input strategy attempts to take advantage of the memory corruption 
vulnerabilities which are known to occur within the PDF file format when the file length
field does not match the streamed object size.  

Potential improvements:
* Implementation of more mutation strategies targeting parser directly
* Use of a more efficient mode for PDF file manipulation as PyPDF2 does not allow for
  enough granularity of metadata manipulation or cloning
* Reportlab module would likely allow for more opportunities for PDF mutations as it 
  allows more control

__JPEG Module__
This module is still very much a work in progress, however, upon selection by the harness
the module successfully converts the sample text file to a stream of bytes to JPEG format.
This is done by the Python PIL library, which has a plethora of functions that allow data
manipulation.
The primary method of vulnerability discovery used by this module is done through the
insertion of special bytes such as 0xFF, 0x00, 0xD8, and 0xD9, as well as through the
flipping of bits randomly throughout the file. File expansion is also done through the PIL
library to attempt to cause a buffer overflow. 

Successful strategies:
* flipping random bits throughout the JPEG data segment
* inserting random control bits throughout all regions of the file, with exception 
  first and last two bytes to maintain file validity

Potential improvements:
* PIL does not easily give control of JPEG metadata
* PIL will throw errors when given a file with embedded null bytes
* insertion of key bytes tends to render the JPEGs invalid by many binaries - limiting
  insertion region may improve this functionality

__JSON Module__
The JSON module, json_fuzzer.py takes a sample input, such as json1.txt, mutates the input
data by maintaining the data types, such as mutating MAXINT to +MAXINT but maintaining the
integer type. There is also a test for null case where data is nullified according to 
their data type, e.g. an integer field will become 0 and a list field will become an empty
list []. Inversely, some mutated input changes the data type, such as converting a
Boolean value to an integer field. These payloads are sent to the binary, and which waits
for a return code, such as -11 (SIGSEGV) and other non-zero error code.
For every iteration, there are 2 ways of generating payload: using the original sample 
input or chaining the payload of the previous iteration as an input.

__TXT Module__
The plaintext module places an emphasis on producing a wide variety of inputs, as well as 
generation of inputs containing key characters. Of the different modules, this one can
take advantage of the insertion of control characters and format string mutations the 
most to produce segmentation faults and overflow events. 

Successful strategies: 
* known int technique 
* bit flipping of sample input
* byte flipping
* key word fuzzing

Potential improvements:
* random control bit insertion

__XML Module__
This module is selected by the handler following the input of a XML file as the sample
input. This method successfully causes the segmentation fault of binaries by targeting the
vulnerabilities of the element tree format, generating strategies and permutations which 
reflect this.

Successful Strategies:
* Format string injection
* Depth-wise node breeding
* Large input generation

Of the above strategies, the depth-wise breeding process is unique to XML in that it works
by spawning child nodes both recursively and at random times to cause buffer overflow 
events resulting in segmentation fault, and thus data leakage. 

Potential improvements: 
* Improved function logic to reduce the dependency on nested loops
* Complete implementation of key-word extraction
* Implementation coverage based mutations
* Implementation of repeated-parts based mutations
 

__Code Coverage__
This module takes in the binary from the Harness and finds all the relevant functions to use as break-points.
Using a python libary known as ptrace, we attach the subprocess to a ptrace-debugger. When the debugger is run
we check for each breakpoint event and count the instructions "visited" in a set data structure. 

After we segfault we use this set and the number of breakpoint ratio to calculate the "functional" code coverage.
While this worked for some binaries, it hanged for the others. So we decided to keep it out of our harness logic,
to ensure the fuzzer's experience was consistent. The code can be seen Coverage.py class.


Potential improvements: 
* Improving stdin piping, this seems to be where the crash is happening. 
* Exploring other libraries such as qumeu to improve performance. 
* Implementation of coverage based mutations



__Reflection__
Overall, the development of the fuzzer and the associated modules has been a success. 
The CSV, JSON, TXT, JSON, and XML modules have proven to be able to reliably produce 
useful errors such as hangs, segmentation faults, and infinite loops on a plethora of 
binaries. The unique methods required by these file types were challenging and exciting
to learn and implement - broadening the scope of understanding and skillsets at our
disposal. Whilst the experience was invaluable, the fuzzer itself has proven to be a 
useful tool for CTFs and vulnerability discovery. 

The analytics provided by the dumping of the core-file information allows for the 
extraction and use of the symbols within the target binary for further exploitation. This
is evident by the dumping of information pertaining to the memory address corresponding to
EIP at the time of the crash. In a scenario where a win() function exists, using the 
successful payload to calculate appropriate offsets could theoretically allow for the 
immediate jumping to the address of win(), with use of the dumped EIP. 

That said, the project proved to be a challenge across each of the file types, as evident
by the incomplete functionality. The likes of JPEG and PDF were not completed in their 
entirety, and ELF was not implemented at all. This was due to an issue with the complexity
of the types, the amount of time needed to debug and implement the functions of the 
mid-point check-in, and the lack of clear information on the vulnerabilities of these 
types of files. It was also an issue that many of the Python libraries pertaining to these
types had a large degree of builtin error checking, or did not allow easy manipulation of 
file metadata. This made the process of implementing mutation strategies difficult. 

Code-coverage was another shortcoming of the fuzzer, as it was frequently working at a
surface level of the target binaries, though was frequently running into issues with race
conditions. This functionality proved to be finicky, and would likely throw errors that 
would cause the fuzzer to crash. Clearly, with more time and effort it would be possible
produce a more robust system, especially in line with the improvements suggested for each
of the file types. 


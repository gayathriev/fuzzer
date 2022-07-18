Fuzzer
========

## Team Members
| Name                   | zID      |
| ---------------------- |----------|
| Mae Vuong              | z5286353 |
| Edmund O'Ryan          | z5114478 |
| James He               | z5161088 |
| Gayathrie Vijayalingam | z5193713 |
| Kenneth Mejico         | z5257133 |

## Fuzzer (30 marks)

Fuzzing is an automated software testing technique that involves providing invalid, unexpected, or random data as inputs to a computer program. **The program is then monitored for exceptions** such as crashes, failing built-in code assertions, or potential memory leaks.  **An effective fuzzer generates semi-valid inputs that are "valid enough"** in that they are not directly rejected by the parser, but do create unexpected behaviors deeper in the program and are "invalid enough" to expose corner cases that have not been properly dealt with.

For this project you will be required to implement a black box fuzzer, that given a binary containing a single vulnerability and a file containing one valid input to the binary, will need to find a valid input that causes an incorrect program state to occur (crash, invalid memory write, heap UAF, etc).

The main goal of your fuzzer should be to touch as many codepaths as possible within the binary by either mutating the supplied valid input or generating completely new input (empty files, null bytes, really big files, etc).

### Mark Breakdown
-   10 marks - **General Fuzzer**
    -   Find all vulnerabilities in the 11 provided binaries
    -   Writing test vulnerable binaries to test your fuzzer
-   10 marks - **Fuzzer Functionality**
    -   Mutation Strategies
        -   bit flips, byte flips, known ints, repeated parts, keyword extraction, arithmetic, coverage based mutations
    -   Understanding and manipulation of file formats (Manipulating file headers, field names, data structures, etc)
        -   JSON, CSV, XML, JPEG, ELF, PDF
-   10 marks - **Harness Functionality**
    -   Detecting the type of crash (2 marks)
    -   Detecting Code Coverage (2 marks)
    -   Avoiding overheads (2 marks)
        -   Not creating files
        -   In memory resetting (Not calling execve)
    -   Useful logging / statistics collection and display (2 marks)
    -   Detecting Hangs / Infinite loops (2 marks)
-   Bonus (6 marks) - **Something awesome**
    -   Something cool your fuzzer does

## Documentation (10 marks)
Fuzzer design and functionality (around 1-2 pages)

-   How your fuzzer works
    -   Describe both in detail the different mutation strategies you use, as well as the Harness's capabilities
-   What kinds of bugs your fuzzer can find
-   What improvements can be made to your fuzzer (Be honest. We won't dock marks for things you didn't implement. This shows reflection and understanding)

## Assignment Check In (10 marks)
In week 7, you will need to submit a basic working version of your fuzzer **and** a half page description of your fuzzer. It does not have to the complete functionality of your fuzzer.

We will only test your fuzzer against two binaries ( `csv1, json1` ). 

We will run `./fuzzer program sampleinput.txt` to test your fuzzer.

### Mark Breakdown
-   (6 marks) Find a vulnerability in the `csv1 and json1` binaries.
-   (4 marks) Half page description of your fuzzer functionality so far and the fuzzer design [ **writeup.md** ].

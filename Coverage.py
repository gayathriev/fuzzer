from signal import *
from pwn import *
from pwnlib import *
import subprocess
import os
import os.path
import time
from ptrace import debugger


class Coverage():
    def __init__(self, binary):
        self.binary = binary
        self.visited_instr = set()
        self.break_points = []
        self.elf = ELF('./' + binary)
    
    def make_break_points(self):
        symbols = self.elf.symbols
        functions = {}
        for key in symbols:
            if(key[:1] != "." and key[:1] != "_" and key[:4] != "got." and key[:4] != "plt." and ("GLIBC" not in key) and key != "deregister_tm_clones" and key != "register_tm_clones" and key !=""):
                functions[key] = symbols[key]
        
        for func in filtered_functions:
            add = hex(functions[func])
            self.break_points.append(add)


    def run(self, data):

        # DFILE = "mutated.txt"
        # try:
        #     os.mkfifo(DFILE, mode=0o777)
        # except FileExistsError:
        #     pass
        # input_subprocess = os.open(DFILE, os.O_RDONLY | os.O_NONBLOCK)

        # comm = os.open(DFILE, os.O_WRONLY)
        # process = subprocess.Popen(
        #     [self.binary],
        #     # shell=False,
        #     stdout=open(os.devnull,'wb'),
        #     stdin=input_subprocess,
        #     stderr=PIPE,
        #     close_fds=True,
        #     preexec_fn = os.setsid
        # )

        # os.close(input_subprocess)
        # try:
        #     os.write(comm, bytes(data,'utf-8'))
        # except:
        #     os.close(comm)
        #     os.unlink(DFILE)
        #     return

        # os.close(comm)
        # os.unlink(DFILE)

        proc = subprocess.Popen(
					self.binary,
					stdin  = subprocess.PIPE,
					stdout = subprocess.PIPE,
					stderr = subprocess.PIPE,
		)

        
        proc.communicate(data.encode())
        pid = proc.pid
        ptracer = debugger.PtraceDebugger()
        
        try:
            trace_process = ptracer.addProcess(pid, False)
            if self.break_points:
                for add in self.break_points:
                    trace_process.createBreakpoint(int(add,16), size = 4)
            while True:
                trace_process.cont()
                trace_process_event = ptracer.waitProcessEvent()
                sig_num = trace_process_event.signum
                if sig_num == signal.SIGTRAP:
                    instrPtr = trace_process.getInstrPointer()
                    self.visited_instr.add(instrPtr - 1)
                    trace_process.setInstrPointer(instrPtr-1)
                    brkPts = trace_process.findBreakpoint(instrPtr-1).desinstall()
                elif sig_num == signal.SIGINT or sig_num == signal.SIGSEGV or sig_num == signal.SIGABRT or sig_num == signal.SIGFPE:
                    trace_process.detach()
                    break
                elif isinstance(trace_process_event, debugger.ProcessExit):
                    trace_process.detach()
                    break
        except:
            return
    
    def calculate_coverage(self):
        total = len(self.break_points)
        visited = len(self.visited_instr)

        return (visited/total)*100

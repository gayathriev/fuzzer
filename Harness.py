from signal import signal, SIGINT
from pwn import *
from pwnlib import *
import subprocess
import time
from ptrace import debugger
from Coverage import Coverage
from support import detect
from support.generate_summary import prepare_summary_success
from support.generate_summary import prepare_summary_fail


class Harness():
	def __init__(self, binary):
		self.binary = binary
		self.aborts = 0
		self.hangs = 0
		self.iterations = 0
		self.start_time = time.time()
		self.my_coverage = Coverage(binary)

		self.my_coverage.make_break_points()

	def no_summary(self):
		total_time = time.time()  - self.start_time
		prepare_summary_fail(self.hangs, self.aborts, self.iterations, total_time)

	def start_process(self, payload):
		with subprocess.Popen(
					self.binary,
					stdin  = subprocess.PIPE,
					stdout = subprocess.PIPE,
					stderr = subprocess.PIPE,
		) as proc:

			#self.my_coverage.run(pid)
			proc.communicate(payload.encode())
			self.iterations = self.iterations + 1
			
			self.my_coverage.run(payload)
			res = proc.wait(timeout=0.5)


			if ((res is None) or res == 3 or (res < 0 and res != -11)):
				live = proc.poll()
				if (live is None):
					log.critical('Process hangs')
					self.hangs = self.hangs + 1
				else:
					log.critical('Process aborted')
					self.aborts = self.aborts + 1
			returncode = proc.returncode
			if returncode == -11:
				''' check this '''
				total_time = time.time() - self.start_time
				coverage = self.my_coverage.calculate_coverage()
				print(coverage)
				prepare_summary_success(self.hangs, self.aborts, self.iterations, total_time)
				# print("in here")
				# p = process(self.binary)
				# p.sendline(payload.encode())
				# core = Coredump('./core')
				# print(core)
			return returncode
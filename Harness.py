from signal import signal, SIGINT
from pwn import *
from pwnlib import *
import subprocess
from support import detect

class Harness():
	def __init__(self, binary):
		self.binary = binary
	def start_process(self, payload):
		""" start a process to binayy """
		with subprocess.Popen(
					self.binary,
					stdin  = subprocess.PIPE,
					stdout = subprocess.PIPE,
					stderr = subprocess.PIPE,
		) as proc:

			proc.communicate(payload.encode())
			res = proc.wait(timeout=0.5)
			if ((res is None) or res == 3 or (res < 0 and res != -11)):
				live = proc.poll()
				if (live is None):
					log.critical('Process hangs')
				else:
					log.critical('Process aborted')
			returncode = proc.returncode
			if returncode == -11:
				print("in here")
				p = process(self.binary)
				p.sendline(payload.encode())
				core = Coredump('./core')
				print(core)
			return returncode

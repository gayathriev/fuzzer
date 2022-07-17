from signal import signal, SIGINT
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
			return proc.returncode


@ TODO 
'''
Check process health
'''


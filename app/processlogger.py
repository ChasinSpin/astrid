import sys
import signal
#from multiprocessing import Process, Queue, current_process
import multiprocessing
from logging.handlers import QueueHandler
import logging


LOGGING_LEVEL = logging.DEBUG


# Singleton

class ProcessLogger:

	APP = __name__

	__instance = None

	def __init__(self, log_filename: str, logging_level = LOGGING_LEVEL):
		"""
			Call once from the top process to start the logging process
		"""

		self.logger = None

		if ProcessLogger.__instance != None:
			raise Exception("This class is a singleton!")
		else:
			ProcessLogger.__instance = self

			self.queue = multiprocessing.Queue()

			# Set the MainProcess name of this process
			multiprocessing.current_process().name = 'main'

			# Start the logging process
			self.process = multiprocessing.Process(target = self.main, args = (self.queue, log_filename), name='logging')
			self.process.start()

			self.logger = logging.getLogger(ProcessLogger.APP)
			queueHandler = QueueHandler(self.queue)
			queueHandler.setLevel(logging_level)
			self.logger.addHandler(queueHandler)
			self.logger.setLevel(logging_level)


	@staticmethod
	def getInstance():
		if ProcessLogger.__instance == None:
			return None
		return ProcessLogger.__instance


	def __cleanup_handler(self, sig, frame):
		"""
			Called to cleanup when the process exits
		"""
		self.logger.info('logging process terminated')
		self.logger.info('-------------------- END SESSION --------------------')
		sys.exit(0)


	def main(self, queue, log_filename):
		"""
			The seperate process that does the logging
		"""
		# Setup signal handler so that process signals (e.g. CTRL-C) can kill the process
		signal.signal(signal.SIGINT, self.__cleanup_handler)
		signal.signal(signal.SIGTERM, self.__cleanup_handler)

		# Create the logger
		self.logger = logging.getLogger(ProcessLogger.APP)

		# Create formatter
		formatter = logging.Formatter("%(asctime)s %(processName)-11s %(levelname)-8s %(message)s", "%Y-%m-%d %H:%M:%S")

		# Create Console handler
		consoleHandler = logging.StreamHandler(stream=sys.stderr)
		consoleHandler.setFormatter(formatter)
		consoleHandler.setLevel(logging.DEBUG)

		# Create File handler
		fileHandler = logging.FileHandler(log_filename)
		fileHandler.setFormatter(formatter)
		fileHandler.setLevel(logging.DEBUG)

		# Add handlers to logger
		self.logger.addHandler(fileHandler)
		self.logger.addHandler(consoleHandler)

		# Set output level
		self.logger.setLevel(logging.DEBUG)

		self.logger.info('-------------------- NEW SESSION --------------------')
		self.logger.info('logging process started')

		# Loop waiting and processing logging requests
		while True:
			message = queue.get()
			if message is None:	# Sentinel message to exit process
				break
			elif isinstance(message, dict):
				if message['cmd'] == 'change_file':
					self.logger.removeHandler(fileHandler)

					fileHandler2 = logging.FileHandler(message['fname'])
					fileHandler2.setFormatter(formatter)
					fileHandler2.setLevel(logging.DEBUG)
					self.logger.addHandler(fileHandler2)

					consoleHandler.setLevel(logging.INFO)
				elif message['cmd'] == 'revert':
					self.logger.removeHandler(fileHandler2)
					fileHandler2.close()
					self.logger.addHandler(fileHandler)
					consoleHandler.setLevel(logging.DEBUG)
			else:
				self.logger.handle(message)

		self.logger.info('Logging process shutting down')

		# Exit and cleanup
		self.__cleanup_handler(None, None)


	def terminate(self):
		"""
			Call once from the top process to stop the logging process and terminate the logging process
		"""
		self.queue.put(None)
		self.process.join()


	@classmethod
	def  startChildLogging(cls, queue_logging: multiprocessing.Queue, name: str, logging_level = LOGGING_LEVEL):
		"""
			Call from a child process to add logging
		"""
		# Set the name of this process
		multiprocessing.current_process().name = name 

		logger = logging.getLogger(ProcessLogger.APP)

		queueHandler = QueueHandler(queue_logging)
		queueHandler.setLevel(logging_level)
		logger.addHandler(queueHandler)
		logger.setLevel(logging_level)

		logger.info('logging started for child process: %s' % name)
		
		return logger


	def getLogger(self):
		return self.logger


	def setPropagate(self, enable):
		self.logger.propagate = enable

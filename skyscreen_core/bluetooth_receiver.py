import serial
import json
import cStringIO

# Parameters for an individual pattern.
# Right now, only 4 separate numeric parameters are given by the Control Board app
# We can extend these later to give more parameters, or have the parameters named
class PatternParams(object):
	index = 0
	p1    = 0
	p2    = 0
	p3    = 0
	p4    = 0

# Holds the parameters for the left and right pattern parameters from the Control Board app,
# as well as overall brightness, tempo, and crossfade values.
#
# If the parameters are being read from the command line, read until the closing right brace ('}'),
# and pass the text into the "parse" method.
class SkyScreenParams(object):
	def __init__(self):
		self.brightness = 0
		self.tempo      = 0
		self.crossfade  = 0

		self.patternA = PatternParams()
		self.patternB = PatternParams()

	# Parse JSON string and extract values into class attributes.
	# The text can come from anywhere at this point (command line or serial port)
	def parse(self, values):
		self.patternA.index = values["patternA"]
		self.patternA.p1    = values["a0"]
		self.patternA.p2    = values["a1"]
		self.patternA.p3    = values["a2"]
		self.patternA.p4    = values["a3"]

		self.patternB.index = values["patternB"]
		self.patternB.p1    = values["b0"]
		self.patternB.p2    = values["b1"]
		self.patternB.p3    = values["b2"]
		self.patternB.p4    = values["b3"]

		self.brightness  = values["brightness"]
		self.tempo       = values["tempo"]
		self.crossfade   = values["crossFade"]


# Reads a parameter structure from serial port.
# Right now it reads one JSON structure and returns it back,
# eventually it will be a separate thread which constantly reads parameters and refreshes the application
class SerialInput(object):
	def __init__(self, port):
		self.port = port
		self.buffer = cStringIO.StringIO()
		self.serial_connection = None
		self.current_data = None

	def __enter__(self):
		self.serial_connection = serial.Serial(
			port=self.port,
			baudrate=115200,
			bytesize=serial.EIGHTBITS,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			timeout=1)
		self.serial_connection.__enter__()
		self.current_data = SkyScreenParams()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.serial_connection.__exit__(exc_type, exc_val, exc_tb)

	def read_params(self):
		chars_waiting = self.serial_connection.inWaiting()
		while chars_waiting:
			char = self.serial_connection.read(1)
			self.buffer.write(char)
			if char == '}':
				self.buffer.seek(0, 0)
				new_data = json.load(self.buffer)
				self.current_data.parse(new_data)
				self.buffer = cStringIO.StringIO()

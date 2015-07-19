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
	brightness = 0
	tempo      = 0
	crossfade  = 0

	patternA = PatternParams()
	patternB = PatternParams()

	# Parse JSON string and extract values into class attributes.
	# The text can come from anywhere at this point (command line or serial port)
	def parse(jsonData):
		values = json.loads(jsonData)

		self.patternA.index = values["patternA"];
		self.patternA.p1    = values["a0"];
		self.patternA.p2    = values["a1"];
		self.patternA.p3    = values["a2"];
		self.patternA.p4    = values["a3"];

		self.patternB.index = values["patternB"];
		self.patternB.p1    = values["b0"];
		self.patternB.p2    = values["b1"];
		self.patternB.p3    = values["b2"];
		self.patternB.p4    = values["b3"];

		self.brightness  = values["brightness"];
		self.tempo       = values["tempo"];
		self.crossfade   = values["crossFade"];

# Reads a parameter structure from serial port.
# Right now it reads one JSON structure and returns it back,
# eventually it will be a separate thread which constantly reads parameters and refreshes the application
class SerialReader(object):
	serialPort = "\\.\COM4"

	def __init__(port):
		self.serialPort = port

	def readParams():
		ser = serial.Serial(port=serialPort, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
		incoming = ""
		c = ser.read(1)
		while c != '}':
			incoming += c
		    c = ser.read(1)
		incoming += '}'
		data = ''.join(incoming)
		return json.loads(data)

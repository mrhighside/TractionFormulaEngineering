import sys
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

import RPi.GPIO as GPIO

# This class has all the hardware interface funtions
#might need to break it apart at some point

#TODO: pass in configuration with all PIN values and potSensitivity
class HardwareInterface:
	def __init__(self):
		#Setup Led
		self.LED_PIN = 19
		self.RED_LED_PIN = 21
		self.GREEN_LED_PIN = 12
		self.BLUE_LED_PIN = 26

		self.potSensitivity = 250

		self.currentLightOn = False

		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self.LED_PIN,GPIO.OUT)

		#setup button
		self.button1 = digitalio.DigitalInOut(board.D23)
		self.button1.direction = digitalio.Direction.INPUT
		self.button1.pull = digitalio.Pull.UP

		GPIO.setup(self.RED_LED_PIN,GPIO.OUT)
		GPIO.setup(self.GREEN_LED_PIN,GPIO.OUT)
		GPIO.setup(self.BLUE_LED_PIN,GPIO.OUT)

		#turn off
		GPIO.output(self.RED_LED_PIN, GPIO.HIGH)
		GPIO.output(self.GREEN_LED_PIN, GPIO.HIGH)
		GPIO.output(self.BLUE_LED_PIN, GPIO.HIGH)

		# create the spi bus
		spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

		# create the cs (chip select)
		cs = digitalio.DigitalInOut(board.D22)

		# create the mcp object
		mcp = MCP.MCP3008(spi, cs)

		# create an analog input channel on pin 0
		self.chan0 = AnalogIn(mcp, MCP.P0)

		self.last_read = 0

		self.lastButtonValue = False

		self.turnIndicatorLightOff()

	def doInitilazationTest(self):
		#go through some stuff to make sure shit is working.
		#return false for error
		print("Running Hardware Interface tests...")
		#tests go here.
		print("Hardware Interface tests complete.")
		return True

	def isModeChange(self):
		#buttons are backwards
		buttonValue = not self.button1.value

		if buttonValue == True and buttonValue != self.lastButtonValue:
			self.lastButtonValue = buttonValue
			return True
		else:
			self.lastButtonValue = buttonValue
			return False

	def setColorLED(self, color="off"):
		red = GPIO.HIGH
		green = GPIO.HIGH
		blue = GPIO.HIGH

		if color == "purple":
			red = GPIO.LOW
			blue = GPIO.LOW
		elif color == "red":
			red = GPIO.LOW
		elif color == "blue":
			blue = GPIO.LOW
		elif color == "green":
			green = GPIO.LOW
		elif color == "yellow":
			red = GPIO.LOW
			green = GPIO.LOW 


		GPIO.output(self.RED_LED_PIN, red)
		GPIO.output(self.GREEN_LED_PIN, green)
		GPIO.output(self.BLUE_LED_PIN, blue)

	def normalizeValues(self, value, left_min, left_max, right_min, right_max):
		# this remaps a value from original (left) range to new (right) range
		# Figure out how 'wide' each range is
		left_span = left_max - left_min
		right_span = right_max - right_min

		# Convert the left range into a 0-1 range (int)
		valueScaled = int(value - left_min) / int(left_span)

		# Convert the 0-1 range into a value in the right range.
		return int(right_min + (valueScaled * right_span))

	def turnIndicatorLightOn(self):
		GPIO.output(self.LED_PIN,GPIO.HIGH)

	def turnIndicatorLightOff(self):
		GPIO.output(self.LED_PIN,GPIO.LOW)

	def handleIndicatorSwitch(self):

		# we'll assume that the pot didn't move
		trim_pot_changed = False

		# read the analog pin
		trim_pot = self.chan0.value

		# how much has it changed since the last read?
		pot_adjust = abs(trim_pot - self.last_read)

		if pot_adjust > self.potSensitivity:
			trim_pot_changed = True

		if trim_pot_changed:
			# convert 16bit adc0 (0-65535) trim pot read into 0-100 volume level
			normalizedTrimPot = self.normalizeValues(trim_pot, 0, 65535, 0, 100)

			if normalizedTrimPot > 50 and not self.currentLightOn:
				#print("LED on")
				self.currentLightOn = True
				self.turnIndicatorLightOn()
			elif normalizedTrimPot <= 50 and self.currentLightOn:
				#print ("LED off")
				self.currentLightOn = False
				self.turnIndicatorLightOff()

			# save the potentiometer reading for the next loop
			self.last_read = trim_pot

	def cleanup(self):
		GPIO.cleanup()
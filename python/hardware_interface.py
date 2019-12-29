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
		nonlocal LED_PIN
		nonlocal RED_LED_PIN
		nonlocal GREEN_LED_PIN
		nonlocal BLUE_LED_PIN

		nonlocal potSensitivity
		potSensitivity = 250

		nonlocal currentLightOn
		currentLightOn = False

		turnIndicatorLightOff(self)

		LED_PIN = 19
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(LED_PIN,GPIO.OUT)

		#setup button
		button1 = digitalio.DigitalInOut(board.D23)
		button1.direction = digitalio.Direction.INPUT
		button1.pull = digitalio.Pull.UP

		RED_LED_PIN = 21
		GREEN_LED_PIN = 12
		BLUE_LED_PIN = 26

		GPIO.setup(RED_LED_PIN,GPIO.OUT)
		GPIO.setup(GREEN_LED_PIN,GPIO.OUT)
		GPIO.setup(BLUE_LED_PIN,GPIO.OUT)

		#turn off
		GPIO.output(RED_LED_PIN, GPIO.HIGH)
		GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
		GPIO.output(BLUE_LED_PIN, GPIO.HIGH)

		# create the spi bus
		spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

		# create the cs (chip select)
		cs = digitalio.DigitalInOut(board.D22)

		# create the mcp object
		mcp = MCP.MCP3008(spi, cs)

		# create an analog input channel on pin 0
		chan0 = AnalogIn(mcp, MCP.P0)

		print('Raw ADC Value: ', chan0.value)
		print('ADC Voltage: ' + str(chan0.voltage) + 'V')

	def doInitilazationTest(self):
		#go through some stuff to make sure shit is working.
		#return false for error
		print("Running Hardware Interface tests...")
		#tests go here.
		print("Hardware Interface tests complete.")
		return True

	def isModeChange(self):
		nonlocal lastButtonValue
		lastButtonValue = False

		#buttons are backwards
		buttonValue = not button1.value

		if buttonValue != lastButtonValue:
			return True
		else:
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


		GPIO.output(RED_LED_PIN, red)
		GPIO.output(GREEN_LED_PIN, green)
		GPIO.output(BLUE_LED_PIN, blue)

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
		GPIO.output(LED_PIN,GPIO.HIGH)

	def turnIndicatorLightOff(self):
		GPIO.output(LED_PIN,GPIO.LOW)

	def handleIndicatorSwitch(self):

		# we'll assume that the pot didn't move
		trim_pot_changed = False

		# read the analog pin
		trim_pot = chan0.value

		# how much has it changed since the last read?
		pot_adjust = abs(trim_pot - last_read)

		if pot_adjust > potSensitivity:
			trim_pot_changed = True

		if trim_pot_changed:
			# convert 16bit adc0 (0-65535) trim pot read into 0-100 volume level
			normalizedTrimPot = normalizeValues(trim_pot, 0, 65535, 0, 100)

			if normalizedTrimPot > 50 and not currentLightOn:
				print("LED on")
				currentLightOn = True
				turnIndicatorLightOn(self)
			elif normalizedTrimPot <= 50 and currentLightOn:
				print ("LED off")
				currentLightOn = False
				turnIndicatorLightOff(self)

			# save the potentiometer reading for the next loop
			last_read = trim_pot
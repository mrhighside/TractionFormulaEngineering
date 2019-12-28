import json
import os
import os.path
from os import path
import sys
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

import RPi.GPIO as GPIO

#Setup Led
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

#current Mode
selectedMode = 0

def main():

	modesFileName = "modes.json"
	defaultModeNumber = 0

	if len(sys.argv) > 1 and (sys.argv[1].lower() == "help" or sys.argv[1].lower() == "version"):
		printHelpMessage()
		sys.exit(0)

	#print(len(sys.argv))

	if len(sys.argv) > 1:
		modesFileName = sys.argv[1]

	if len(sys.argv) > 2:
		defaultModeNumber = int(sys.argv[2])

	selectedModeNumber = defaultModeNumber
	print("Loading modes from {}, defaulting to modeNumber {}.".format(modesFileName, selectedModeNumber))

	modes = loadModes(modesFileName)

	if len(modes) ==0:
		print("Error! No modes loaded! Exiting!")
	elif len(modes) < selectedModeNumber:
		print("Default mode number to high! Defaulting to 0!")
		selectedModeNumber = 0

	selectedMode = modes[selectedModeNumber]

	#print("Default mode selected: {}".format(selectedMode['modeName']))
	#sensitivity = selectedMode["sensitivity"]
	#print("sensitivity: {}".format(sensitivity))

	print("Using mode: {}.".format(selectedMode['modeName']))

	last_read = 0       # this keeps track of the last potentiometer value
	currentLightOn = False

	try:
		#main Loop
		while True:
			if not button1.value:
				selectedModeNumber = selectedModeNumber + 1

				#only 2 modes
				if selectedModeNumber >= len(modes):
					selectedModeNumber = 0

				selectedMode = modes[selectedModeNumber]
				print("Mode: {} enganged.".format(selectedMode["modeName"]))

			setColorLED(selectedMode["indicatorColor"])
			
			# we'll assume that the pot didn't move
			trim_pot_changed = False

			# read the analog pin
			trim_pot = chan0.value

			# how much has it changed since the last read?
			pot_adjust = abs(trim_pot - last_read)

			if pot_adjust > selectedMode['sensitivity']:
				trim_pot_changed = True

			if trim_pot_changed and selectedMode["modeName"] == "attack":
				# convert 16bit adc0 (0-65535) trim pot read into 0-100 volume level
				normalizedTrimPot = normalizeValues(trim_pot, 0, 65535, 0, 100)

				# set OS volume playback volume
				#print('Volume = {volume}%' .format(volume = set_volume))
				#set_vol_cmd = 'sudo amixer cset numid=1 -- {volume}% > /dev/null' \
				#.format(volume = set_volume)
				#os.system(set_vol_cmd)
				if normalizedTrimPot > 50 and not currentLightOn:
					print("LED on")
					currentLightOn = True
					GPIO.output(LED_PIN,GPIO.HIGH)
				elif normalizedTrimPot <= 50 and currentLightOn:
					print ("LED off")
					currentLightOn = False
					GPIO.output(LED_PIN,GPIO.LOW)

				# save the potentiometer reading for the next loop
				last_read = trim_pot


			# hang out and do nothing for a half second
			time.sleep(0.125)
	except KeyboardInterrupt:
		GPIO.cleanup()


def setColorLED(color="off"):
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

def normalizeValues(value, left_min, left_max, right_min, right_max):
	# this remaps a value from original (left) range to new (right) range
	# Figure out how 'wide' each range is
	left_span = left_max - left_min
	right_span = right_max - right_min

	# Convert the left range into a 0-1 range (int)
	valueScaled = int(value - left_min) / int(left_span)

	# Convert the 0-1 range into a value in the right range.
	return int(right_min + (valueScaled * right_span))

def loadModes(fileName = "modes.json"):

	print("Loading Modes from {}.".format(fileName))

	safeMode = False
	# read file
	if not path.exists(fileName):
		print("Mode file '{}' not found! ".format(fileName))
		safeMode = True

	if safeMode:
		print("Entering Safe Mode!")
		modes = [{"modeName":"SAFEMODE", "modeNumber":0, "sensitivity":400}]
		return modes

	with open(fileName, 'r') as configFile:
		data=configFile.read()

	# parse file
	configs = json.loads(data)
	configFile.close()
	
	return configs["modes"]

def printHelpMessage():
	print("Usage: python3 {} [<modesFileName.json>][,<defaultMode (int)>".format(os.path.basename(__file__)))
	print("modesFilename defaults to 'modes.json'.")
	print("defaultMode defaults to 0.")

if __name__ == "__main__":
	main()
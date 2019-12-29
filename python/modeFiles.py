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

#custom imports
from traction_control import TractionControl
from stability_control import StabilityControl
from hardware_interface import HardwareInterface


def main():
	nonlocal selectedModeNumber
	nonlocal selectedMode
	nonlocal MODES

	nonlocal interface

	interface = HardwareInterface()

	if interface.doInitilazationTest():
		print("Hardware Interface Ready.")
	else:
		print("Error with Hardware Interface! Exiting!")
		sys.exit(1)

	selectedModeNumber = 0
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

	MODES = loadModes(modesFileName)

	if len(MODES) ==0:
		print("Error! No modes loaded! Exiting!")
	elif len(MODES) < selectedModeNumber:
		print("Default mode number to high! Defaulting to 0!")
		selectedModeNumber = 0

	selectedMode = MODES[selectedModeNumber]

	print("Using mode: {}.".format(selectedMode['modeName']))

	#Init Modules 
	#TODO: Dynamic Module Loading
	tc = TractionControl(selectedMode)

	if tc.doInitilazationTest():
		print("Traction Control Ready.")
	else:
		print("Error with Traction Control! Exiting!")
		interface.setColorLED("red")

	sc = StabilityControl(selectedMode)

	if sc.doInitilazationTest():
		print("Stability Control Ready.")
	else:
		print("Error with Stability Control! Exiting!")
		interface.setColorLED("red")

	last_read = 0       # this keeps track of the last potentiometer value
	currentLightOn = False

	try:
		#main Loop
		while True:
			if interface.isModeChange():
				selectedMode = updateMode()
				setColorLED(selectedMode["indicatorColor"])
				print("Mode: {} enganged.".format(selectedMode["modeName"]))
				
			if selectedMode["useIndicator"] == True
			interface.handleIndicatorSwitch()


			# hang out and do nothing for a half second
			time.sleep(0.125)
	except KeyboardInterrupt:
		GPIO.cleanup()


def updateMode():
	selectedModeNumber = selectedModeNumber + 1

	if selectedModeNumber >= len(MODES):
		selectedModeNumber = 0

	newSelectedMode = MODES[selectedModeNumber]
	return newSelectedMode

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
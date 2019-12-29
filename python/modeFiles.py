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

#Startup function
#handles command line args and kicks off the good stuff
def main():
	#get and run instance of our class
	modesFileName = "modes.json"

	if len(sys.argv) > 1 and (sys.argv[1].lower() == "help" or sys.argv[1].lower() == "version"):
			printHelpMessage()
			sys.exit(0)

	defaultModeNumber = 0
	
	if len(sys.argv) > 1:
		modesFileName = sys.argv[1]

	if len(sys.argv) > 2:
		defaultModeNumber = int(sys.argv[2])

	tfe = TractionFormulaEngineering(modesFileName, defaultModeNumber)

	tfe.start()

class TractionFormulaEngineering:
	#Main Class for All things Awesome

	def __init__(self, modesFileName, defaultModeNumber):
		#get Hardware Interface
		self.interface = HardwareInterface()

		if self.interface.doInitilazationTest():
			print("Hardware Interface Ready.")
		else:
			print("Error with Hardware Interface! Exiting!")
			sys.exit(1)

		self.selectedModeNumber = 0
		
		self.selectedModeNumber = defaultModeNumber
		print("Loading modes from {}, defaulting to modeNumber {}.".format(modesFileName, self.selectedModeNumber))

		self.MODES = self.loadModes(modesFileName)

		if len(self.MODES) ==0:
			print("Error! No modes loaded! Exiting!")
		elif len(self.MODES) < self.selectedModeNumber:
			print("Default mode number to high! Defaulting to 0!")
			self.selectedModeNumber = 0

		self.selectedMode = self.MODES[self.selectedModeNumber]

		#Init Modules - BEFORE we try and engage the mode.
		#TODO: Dynamic Module Loading
		self.tc = TractionControl(self.selectedMode, self.interface)

		if self.tc.doInitilazationTest():
			print("Traction Control Ready.")
		else:
			print("Error with Traction Control! Exiting!")
			self.interface.setColorLED("red")

		self.sc = StabilityControl(self.selectedMode, self.interface)

		if self.sc.doInitilazationTest():
			print("Stability Control Ready.")
		else:
			print("Error with Stability Control! Exiting!")
			self.interface.setColorLED("red")

		#Now we can engage the initial Mode
		self.engageMode(self.selectedMode)

		print("Using mode: {}.".format(self.selectedMode['modeName']))


	def start(self):
		last_read = 0       # this keeps track of the last potentiometer value
		currentLightOn = False

		try:
			#main Loop
			while True:
				if self.interface.isModeChange():
					newMode = self.updateMode()
					#First disenage old Mode
					self.disengageMode(self.selectedMode)
					self.selectedMode = newMode
					#Now Engage the new Mode
					self.engageMode(self.selectedMode)

				#kick off modules this loop
				#TODO: dynamic this
				self.tc.run()
				self.sc.run()

				# hang out and do nothing for a bit
				time.sleep(0.125)
		except KeyboardInterrupt:
			self.interface.cleanup()

	def engageMode(self, currentMode):
		#update all the modules to the new Mode
		#TODO: dynamically do this for all modules
		if self.tc.engageMode(currentMode) and self.sc.engageMode(currentMode):
			self.interface.setColorLED(currentMode["indicatorColor"])
			print("Mode: {} enganged.".format(currentMode["modeName"]))
		else:
			print("Mode failed to engage! GAH!!")
			self.interface.setColorLED("red")
		
	def disengageMode(self, oldMode):
		#update all the modules to the new Mode
		#TODO: dynamically do this for all modules
		if self.tc.disengageMode(oldMode) and self.sc.disengageMode(oldMode):
			print("Mode: {} disenganged.".format(oldMode["modeName"]))
		else:
			print("Mode failed to disengage! GAH!!")
			self.interface.setColorLED("red")

	def updateMode(self):
		self.selectedModeNumber = self.selectedModeNumber + 1

		if self.selectedModeNumber >= len(self.MODES):
			self.selectedModeNumber = 0

		newSelectedMode = self.MODES[self.selectedModeNumber]
		return newSelectedMode

	def loadModes(self, fileName = "modes.json"):

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
	print("modesFileName defaults to 'modes.json'.")
	print("defaultMode defaults to 0.")

if __name__ == "__main__":
	main()
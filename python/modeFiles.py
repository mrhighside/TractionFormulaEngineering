import json
import os.path
from os import path
import sys

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

	print("Loading modes from {}, defaulting to modeNumber {}.".format(modesFileName, defaultModeNumber))

	modes = loadModes(modesFileName)

	if len(modes) ==0:
		print("Error! No modes loaded! Exiting!")
	elif len(modes) < defaultModeNumber:
		print("Default mode number to high! Defaulting to 0!")
		defaultModeNumber = 0

	selectedMode = modes[defaultModeNumber]

	#print("Default mode selected: {}".format(selectedMode['modeName']))
	#sensitivity = selectedMode["sensitivity"]
	#print("sensitivity: {}".format(sensitivity))

	print("Using mode: {}.".format(modes[0]['modeName']))


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
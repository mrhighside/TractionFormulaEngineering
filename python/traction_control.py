import time

class TractionControl:
	
	def __init__(self, selectedMode, interface):
		self.mode = selectedMode
		self.interface = interface
		print("Traction Control Module Loaded.")


	def run(self):
		#update all settings and specifications for the new mode
		if self.mode["useIndicator"] == True:
			self.interface.handleIndicatorSwitch()

	def engageMode(self, mode):
		self.mode = mode
		if self.mode["useIndicator"] == True:
			self.interface.handleIndicatorSwitch()
		return True

	def disengageMode(self, mode):
		#cleanup for a mode here.
		self.interface.turnIndicatorLightOff()
		return True

	def doInitilazationTest(self): 
		#go through some stuff to make sure shit is working.
		#return false for error
		print("Running Traction Control tests...")
		#tests go here.
		self.interface.turnIndicatorLightOn()
		time.sleep(0.25)
		self.interface.turnIndicatorLightOff()
		time.sleep(0.25)
		self.interface.turnIndicatorLightOn()
		time.sleep(0.25)
		self.interface.turnIndicatorLightOff()
		time.sleep(0.25)
		self.interface.turnIndicatorLightOn()
		time.sleep(0.25)
		self.interface.turnIndicatorLightOff()
		print("Traction Control tests complete.")
		return True

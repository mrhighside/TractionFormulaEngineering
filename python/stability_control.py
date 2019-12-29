import time
class StabilityControl:
	
	def __init__(self, selectedMode, interface):
		self.mode = selectedMode
		self.interface = interface

		print("Stability Control Module Loaded.")

	def run(self):
		#Do important stuff here
		something = "done"

	def engageMode(self, mode):
		self.mode = mode
		return True

	def disengageMode(self, mode):
		#cleanup for a mode here.
		return True
		
	def doInitilazationTest(self): 
		#go through some stuff to make sure shit is working.
		#return false for error
		print("Running Stability Control tests...")
		#tests go here.
		self.interface.setColorLED("purple")
		time.sleep(0.25)
		self.interface.setColorLED("red")
		time.sleep(0.25)
		self.interface.setColorLED("yellow")
		time.sleep(0.25)
		self.interface.setColorLED("blue")
		time.sleep(0.25)
		self.interface.setColorLED("green")
		time.sleep(0.25)
		self.interface.setColorLED()
		print("Stability Control tests complete.")
		return True

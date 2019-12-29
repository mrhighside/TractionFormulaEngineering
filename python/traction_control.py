class TractionControl:
	
	def __init__(self, selectedMode):
		self.mode = selectedMode
		print("Traction Control Module Loaded.")

	def doInitilazationTest(self): 
		#go through some stuff to make sure shit is working.
		#return false for error
		print("Running Traction Control tests...")
		#tests go here.
		print("Traction Control tests complete.")
		return True

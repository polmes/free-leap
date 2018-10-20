import Leap
import sys
import threading
import time
from pivy import coin
import FreeCAD # pylint: disable = E0401

# Constants
DELAY = 0.1

class FreeController(threading.Thread):
	def __init__(self):
		self.running = False
		super(FreeController, self).__init__()
	
	def start(self):
		self.running = True
		super(FreeController, self).start()
	
	def run(self):
		self.main()
	
	def stop(self):
		self.running = False
	
	def main(self):
		controller = Leap.Controller()

		# Current orientation
		r0 = FreeCAD.Gui.ActiveDocument.ActiveView.getCameraNode().orientation.getValue().getValue()

		# Initial variables
		prev = controller.frame()
		first = True

		# Loop
		while self.running:
			frame = controller.frame()

			if frame.id > prev.id:
				if len(frame.hands) == 1: # only accept 1 hand
					hand = frame.hands[0]

					if first:
						first = False

						# Basis 1
						d1 = FreeCAD.Vector(hand.direction)
						n1 = FreeCAD.Vector(hand.palm_normal)
					else:
						# Basis 2
						d2 = FreeCAD.Vector(hand.direction)
						n2 = FreeCAD.Vector(hand.palm_normal)
						
						# Rotation
						r1 = FreeCAD.Rotation(d1, d2)
						nt = r1.multVec(n1)
						r2 = FreeCAD.Rotation(nt, n2)
						rt = r2.multiply(r1).inverted()
						
						# FreeCAD
						FreeCAD.Gui.ActiveDocument.ActiveView.getCameraNode().orientation = coin.SbRotation(rt.Q) * coin.SbRotation(r0)
						# FreeCAD.Gui.SendMsgToActiveView("ViewFit") 
				else:
					if not first: # first == False
						first = True
						r0 = FreeCAD.Gui.ActiveDocument.ActiveView.getCameraNode().orientation.getValue().getValue()
						FreeCAD.Gui.SendMsgToActiveView("ViewFit")

			# Update variables
			prev = frame

			# Refresh UI
			FreeCAD.Gui.updateGui()
			time.sleep(DELAY)

if __name__ == "__main__":
	if not hasattr(FreeCAD, 't') or not FreeCAD.t.running:
		FreeCAD.t = FreeController()
		FreeCAD.t.start()
		FreeCAD.Console.PrintMessage("Started LEAP Motion gesture reconition\n")
	else:
		FreeCAD.t.stop()
		FreeCAD.Console.PrintMessage("Stopped LEAP Motion gesture reconition\n")

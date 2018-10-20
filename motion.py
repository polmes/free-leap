import Leap
import sys
import threading
import time
# import numpy as np
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

		currentOrientation = FreeCAD.Gui.ActiveDocument.ActiveView.getCameraNode().orientation.getValue().getValue()
		prevID = 0
		isFirst = True
		# firstFrame = []
		d1 = []
		n1 = []
		while self.running:
			frame = controller.frame()

			if frame.id != prevID:
				if len(frame.hands) == 1:
					print("1 hand")
					hand = frame.hands[0]

					if isFirst:
						isFirst = False
						# firstFrame = frame
						d1 = FreeCAD.Vector(hand.direction)
						n1 = FreeCAD.Vector(hand.palm_normal)
					else:
						d2 = FreeCAD.Vector(hand.direction)
						n2 = FreeCAD.Vector(hand.palm_normal)
						
						r1 = FreeCAD.Rotation(d1, d2)
						nt = r1.multVec(n1)
						r2 = FreeCAD.Rotation(nt, n2)
						rt = r2.multiply(r1).inverted()

						print("rt = " + str(rt))
						print("cO = " + str(currentOrientation))

						# print(direction)
						# print(normal)
						# print("dot: " + str(direction.dot(normal)))
						
						# FreeCAD
						# FreeCAD.Gui.activeView().setCameraOrientation(rt)
						FreeCAD.Gui.ActiveDocument.ActiveView.getCameraNode().orientation = coin.SbRotation(rt.Q) * coin.SbRotation(currentOrientation)
						# FreeCAD.Gui.SendMsgToActiveView("ViewFit") 
				else:
					if not isFirst: # isFirst == False
						isFirst = True
						currentOrientation = FreeCAD.Gui.ActiveDocument.ActiveView.getCameraNode().orientation.getValue().getValue()
						FreeCAD.Gui.SendMsgToActiveView("ViewFit")

			FreeCAD.Gui.updateGui()
			time.sleep(DELAY)

if __name__ == "__main__":
	try:
		FreeCAD.t.stop()
	except:
		pass
		
	FreeCAD.t = FreeController()
	FreeCAD.t.start()

	print("It should be running now")
	print(threading.enumerate())

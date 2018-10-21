import Leap
import sys
import threading
import time
import math
from pivy import coin
import FreeCAD # pylint: disable = E0401

# Constants
DELAY = 0.1 # [s]
STRENGTH = 0.34 # [0-1]
HISPEED = 999 # [mm/s]
OFFSET = 5 # [units]
# YOLO = 0.5 # scale factor
# NEAR = 0.1 # ~1
# FAR = 100 # ~10

class FixedVector(Leap.Vector):
	def __init__(self, val):
		self.mag = val[0] ** 2 + val[1] ** 2 + val[2] ** 2
		super(FixedVector, self).__init__()

	def magnitude(self):
		return math.sqrt(self.mag)

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
		r0 = FreeCAD.Gui.activeView().getCameraNode().orientation.getValue().getValue()

		# Initial variables
		prev = controller.frame()
		first = True
		rt = []
		# pt = []
		clip = coin.SoClipPlane()
		clipping = False

		# Loop
		while self.running:
			frame = controller.frame()

			if frame.id > prev.id:
				if len(frame.hands) > 0: # we need a hand
					hand = frame.hands[0]
					if len(frame.hands) > 1:
						for h in frame.hands:
							if h.is_left:
								if h.id < hand.id: hand = h
							else: # is_right
								if hand.is_right and h.id < hand.id: hand = h

					if hand.grab_strength > STRENGTH:
						if first:
							# Init
							first = False
							r0 = FreeCAD.Gui.activeView().getCameraNode().orientation.getValue().getValue()
							# p0 = FreeCAD.Gui.activeView().getCameraNode().position.getValue().getValue()

							# Basis 1
							d1 = FreeCAD.Vector(hand.direction)
							n1 = FreeCAD.Vector(hand.palm_normal)
							# p1 = FreeCAD.Vector(hand.palm_position)
						else:
							# Basis 2
							d2 = FreeCAD.Vector(hand.direction)
							n2 = FreeCAD.Vector(hand.palm_normal)
							# p2 = FreeCAD.Vector(hand.palm_position)

							# Previous
							rt0 = rt
							# pt0 = pt
							
							# Rotation
							r1 = FreeCAD.Rotation(d1, d2)
							nt = r1.multVec(n1)
							r2 = FreeCAD.Rotation(nt, n2)
							rtni = r2.multiply(r1)
							rt = rtni.inverted()

							# Translation
							# pt = FreeCAD.Vector(p0) - YOLO * FreeCAD.Rotation(r0[0],r0[1],r0[2],r0[3]).multiply(rt).multVec(p2 - p1)

							# Filter noise
							try:
								rtf = coin.SbRotation.slerp(rt0, rt, 0.5)
								# ptf = 1/2 * (pt0 + pt)
							except:
								rtf = rt
								# ptf = pt
							
							# FreeCAD
							FreeCAD.Gui.activeView().getCameraNode().orientation = coin.SbRotation(rtf.Q) * coin.SbRotation(r0)
							# FreeCAD.Gui.activeView().getCameraNode().position = coin.SbVec3f(ptf)
							# FreeCAD.Gui.SendMsgToActiveView("ViewFit") 
					else:
						if not first: # first == False
							first = True
							FreeCAD.Gui.SendMsgToActiveView("ViewFit")
						
						if FixedVector(hand.palm_velocity).magnitude() > HISPEED:
							# Fruit Ninja Mode
							if not clipping:
								print("Caution: Entering Fruit Ninja Mode")
								r0 = FreeCAD.Gui.activeView().getCameraNode().orientation.getValue().getValue()
								direction = coin.SbRotation(r0).multVec(coin.SbVec3f(hand.palm_normal.to_tuple()))
								clip.plane.setValue(coin.SbPlane(direction, OFFSET)) #  set this to control the clipping plane
								FreeCAD.Gui.activeView().getSceneGraph().insertChild(clip, 0)
								clipping = True
							else:
								print("Back to Safety")
								FreeCAD.Gui.activeView().getSceneGraph().removeChild(clip)
								clipping = False
				else:
					if not first: # first == False
						first = True
						FreeCAD.Gui.SendMsgToActiveView("ViewFit")

			# Update variables
			prev = frame

			# Refresh UI
			FreeCAD.Gui.updateGui()
			time.sleep(DELAY)

		FreeCAD.Gui.activeView().getSceneGraph().removeChild(clip)

if __name__ == "__main__":
	if not hasattr(FreeCAD, 't') or not FreeCAD.t.running:
		FreeCAD.t = FreeController()
		FreeCAD.t.start()
		FreeCAD.Console.PrintMessage("Started LEAP Motion gesture reconition\n")
	else:
		FreeCAD.Gui.SendMsgToActiveView("ViewFit")
		# FreeCAD.Gui.activeView().getCameraNode().nearDistance = NEAR;
		# FreeCAD.Gui.activeView().getCameraNode().farDistance = FAR;
		FreeCAD.t.stop()
		FreeCAD.Console.PrintMessage("Stopped LEAP Motion gesture reconition\n")

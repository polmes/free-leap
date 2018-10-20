import Leap
import sys
import threading
import time
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

		prevID = 0
		isFirst = True
		while self.running:
			frame = controller.frame()

			if frame.id != prevID:
				if len(frame.hands) == 1:
					print("1 hand")
					if isFirst:
						isFirst = False
						# firstFrame = frame
					else:
						hand = frame.hands[0]

						direction = hand.direction
						normal = hand.palm_normal

						print(direction)
						print(normal)
			
			FreeCAD.Gui.updateGui()
			time.sleep(DELAY)

if __name__ == "__main__":
	FreeCAD.t = FreeController()
	FreeCAD.t.start()

	print("It should be running now")
	print(threading.enumerate())

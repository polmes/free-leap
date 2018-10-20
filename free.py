# Init
# import FreeCAD
import Leap, sys, thread, time
# from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

class FreeListener(Leap.Listener):
	def on_init(self, controller):
		self.isFirst = True
		self.firstFrame = []
		print("Initialized")

	def on_connect(self, controller):
		print("Connected")

		# Enable gestures
		# controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
		# controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
		# controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
		# controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

	def on_disconnect(self, controller):
		# Note: not dispatched when running in a debugger.
		print("Disconnected")

	def on_exit(self, controller):
		print("Exited")

	def on_frame(self, controller):
		# Get the most recent frame and report some basic information
		frame = controller.frame()

		print("On Frame")

		# print("Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % ()
			#   frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

		# Get hands
		if len(frame.hands) == 1:
			print("1 hand")
			if self.isFirst:
				print("First")
				self.firstFrame = frame
				self.isFirst = False
			else:
				hand = frame.hands[0]
				axis = hand.rotation_axis(self.firstFrame)
				angle = hand.rotation_angle(self.firstFrame)

				print(axis)
				print(angle)

				# axisCAD = FreeCAD.Vector(axis[0], axis[1], axis[2])
				
				# FreeCAD
				# rotation = FreeCAD.Rotation(axisCAD, angle)
				# Gui.activeView().setCameraOrientation(rotation)
		else:
			self.isFirst = True

		# Gui.updateGui()

def main():
	listener = FreeListener()
	controller = Leap.Controller()

	# Have the listener receive events from the controller
	controller.add_listener(listener)

	# print("Running...")
	# i = 0
	# while True:
	# 	i = i + 1
	# 	# wait for shit to happen

	# Keep this process running until Enter is pressed
	print("Press Enter to quit...")
	try:
		sys.stdin.readline()
	except KeyboardInterrupt:
		pass
	finally:
		# Remove the sample listener when done
		controller.remove_listener(listener)

	controller.remove_listener(listener)

if __name__ == "__main__":
	main()

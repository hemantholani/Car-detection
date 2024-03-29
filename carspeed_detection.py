import cv2
import dlib
import time
import threading
import math

carCascade = cv2.CascadeClassifier('./myhaar.xml')
video = cv2.VideoCapture('./ch01_20181127091944.mp4')

WIDTH = 720
HEIGHT = 560
carWidht = 1.85

# def carNumber(carNum, cID):
	# time.sleep(2)
	# carNum[cID] = 'Car ' + str(cID)


def estimateSpeed(location1, location2, mySpeed,fps):
	d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
	ppm = location2[2] / carWidht
	d_meters = d_pixels / ppm
	speed = mySpeed + d_meters * fps * 3.6
	return speed
	
def trackMultipleObjects():
	rectangleColor = (0, 0, 255)
	frameCounter = 0
	currentCarID = 0
	fps = 0
	
	carTracker = {}
	carNumbers = {}
	carLocation1 = {}
	carLocation2 = {}
	
	while True:
		start_time = time.time()
		rc, image = video.read()
		if type(image) == type(None):
			break
		
		image = cv2.resize(image, (WIDTH, HEIGHT))
		resultImage = image.copy()
		
		frameCounter = frameCounter + 1
		carIDtoDelete = []
		for carID in carTracker.keys():
			trackingQuality = carTracker[carID].update(image)
			
			if trackingQuality < 7:
				carIDtoDelete.append(carID)
				
		for carID in carIDtoDelete:
			print ('Removing carID ' + str(carID) + ' from list of trackers.')
			print ('Removing carID ' + str(carID) + ' previous location.')
			print ('Removing carID ' + str(carID) + ' current location.')
			carTracker.pop(carID, None)
			carLocation1.pop(carID, None)
			carLocation2.pop(carID, None)
		
		if not (frameCounter % 10):
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			cars = carCascade.detectMultiScale(gray, 1.1, 13, 0, (24, 24))
			
			for (_x, _y, _w, _h) in cars:
				x = int(_x)
				y = int(_y)
				w = int(_w)
				h = int(_h)
			
				x_bar = x + 0.5 * w
				y_bar = y + 0.5 * h
				
				matchCarID = None
			
				for carID in carTracker.keys():
					trackedPosition = carTracker[carID].get_position()
					
					t_x = int(trackedPosition.left())
					t_y = int(trackedPosition.top())
					t_w = int(trackedPosition.width())
					t_h = int(trackedPosition.height())
					
					t_x_bar = t_x + 0.5 * t_w
					t_y_bar = t_y + 0.5 * t_h
					
					
				
					if ((t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)) and (x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + h))):
						matchCarID = carID
				
				if matchCarID is None:
					print ('Creating new tracker ' + str(currentCarID))
					
					tracker = dlib.correlation_tracker()
					tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))
					
					carTracker[currentCarID] = tracker
					carLocation1[currentCarID] = [x, y, w, h]
					
					currentCarID = currentCarID + 1

		cv2.putText(resultImage, 'Car count: ' + str(int(currentCarID)), (30, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        
		for carID in carTracker.keys():
			trackedPosition = carTracker[carID].get_position()
					
			t_x = int(trackedPosition.left())
			t_y = int(trackedPosition.top())
			t_w = int(trackedPosition.width())
			t_h = int(trackedPosition.height())
			
			cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), rectangleColor, 2)
			
			# speed estimation
			carLocation2[carID] = [t_x, t_y, t_w, t_h]
				
			
		end_time = time.time()
		if not (end_time == start_time):
			fps = 1.0/(end_time - start_time)
		cv2.putText(resultImage, 'FPS: ' + str(int(fps)), (620, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
		for i in carLocation1.keys():
			if frameCounter % 10 == 0:
				[x1, y1, w1, h1] = carLocation1[i]
				[x2, y2, w2, h2] = carLocation2[i]
				carLocation1[i] = [x2, y2, w2, h2]
				if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
					speed = estimateSpeed([x1, y1, w1, h1], [x2, y2, w2, h2], 0, fps)
					cv2.putText(resultImage, str(int(speed)) + " km/hr", (int(x1 + w1/2), int(y1-5)),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
					print ('CarID ' + str(i) + ' speed is ' + str("%.2f" % round(speed, 2)) + ' km/h.\n')
		cv2.imshow('result', resultImage)
				
		if cv2.waitKey(33) == 27:
			break
	
	cv2.destroyAllWindows()

trackMultipleObjects()
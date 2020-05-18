import numpy as np
import cv2

azulClaro  = np.array([0, 0, 0], dtype = "uint8")
azulEscuro = np.array([100, 200, 200], dtype = "uint8")

camera = cv2.VideoCapture('teste1.mp4')


while True:
	(sucesso,frame) = camera.read()
	if not sucesso:
		break

	obj = cv2.inRange(frame, azulClaro, azulEscuro)
	obj = cv2.GaussianBlur(obj, (3, 3), 0)
	(cnts, _) = cv2.findContours(obj.copy(),	cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	cv2.waitKey(0)

	if len(cnts) > 0:
		print("asd")
		cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
		rect = np.int32(cv2.boxPoints(cv2.minAreaRect(cnt)))
		cv2.drawContours(frame, [rect], -1, (0, 255, 255), 2)
	
	cv2.imshow("Tracking", frame)
	cv2.imshow("Binary", obj)
	if cv2.waitKey(1) & 0xFF == ord("q"):
		break
camera.release()
cv2.destroyAllWindows()

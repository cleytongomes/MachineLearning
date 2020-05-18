

# IMPORTAÇÃO DAS BIBLIOTECAS
import paho.mqtt.client as paho
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import random


# IP DO BROKER
broker="********"

# IDENTIFICADOR MÁQUINA
identificador = "disp_teste_" + str(random.randint(0, 99999))


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())

vs = 0
fp = 0

# PARÂMETROS
min_area = 1000
ultima_atualizacao_estado = int(time.time())
tempo_atualizacao_frame = int(time.time())
text = "PARADA"
cache_motion = []

for x in range(1000):
	cache_motion.append(0)

def organiza_lista(elemento):
	for x in range(len(cache_motion) - 1):
		cache_motion[x] = cache_motion[x + 1]
	cache_motion[len(cache_motion) - 1] = elemento


# CRIA O CLIENT COM O SEU ID
client= paho.Client(identificador)

# CONFIGURAÇÕES DE ACESSO
client.username_pw_set("**", password="****")
client.connect(broker)

# INICIA O LOOP
client.loop_start()

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
	vs = VideoStream(src=0).start()
	time.sleep(2.0)
# otherwise, we are reading from a video file
else:
	vs = cv2.VideoCapture(args["video"])

# initialize the first frame in the video stream
firstFrame = None

# loop over the frames of the video
while True:

	# PEGA O FRAME ATUAL
	frame = vs.read()
	frame = frame if args.get("video", None) is None else frame[1]
	
	# VERIFICA O BUFFER PARA INDICAR SE A MÁQUINA ESTÁ LIGADA OU DESLIGADA
	if(sum(cache_motion) < 900):
		if(text == "EM TRABALHO"):
			client.publish("3F/TESTE/", "PAUSADA");
		text = "PARADA"
	else:
		if(text == "PARADA"):
			client.publish("3F/TESTE/", "INICIADA");
		text = "EM TRABALHO"

	# VERIFICA SE CHEGOU AO FINAL DO VÍDEO, FRAME NONE
	if frame is None:
		break

	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# SE O PRIMEIRO FRAME NÃO ESTIVER PREENCHIDO, PREENCHE ELE
	if firstFrame is None :
		firstFrame = gray
		continue

	# CALCULA A DIFERENÇA DO PRIMEIRO FRAME COM O ATUAL
	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	v_contorno = False
	# LOOP NOS CONTORNOS
	for c in cnts:

		# IGNORA CONTORNOS MENORES QUE UMA ÁREA ESPECÍFICA
		if cv2.contourArea(c) < min_area:
			continue

		v_contorno = True
		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		ultima_atualizacao_estado = int(time.time())

	if(v_contorno):
		organiza_lista(1)
	else:
		organiza_lista(0)

	print(cache_motion)

	# draw the text and timestamp on the frame
	cv2.putText(frame, "status maquina: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

	# show the frame and record if the user presses a key
	cv2.imshow("Live", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break

	if(tempo_atualizacao_frame + 1 < int(time.time())):
		tempo_atualizacao_frame = int(time.time())
		firstFrame = gray

# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()
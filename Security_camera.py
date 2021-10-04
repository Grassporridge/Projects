#Code to detect people/objects on the camera and store videos of them
#Modifiers to display identified objects and to mail the identified objects

import cv2
import time
from datetime import datetime as dt
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')


def Mail_img(from_add='xyz@xyz.com',password='abcdef', to_add='zyx@zyx.com'):
	#Creates a file with the identified object and mails it to given mail address
	#Have to turn on less secure device access if using gmail account

	if not(os.path.exists("objects")):
		os.mkdir("objects")
	cur_time = dt.now().strftime("%b%d_%H-%M-%S")
	cv2.imwrite(os.path.join("objects",f'{cur_time}.jpg'),frame)

	msg = MIMEMultipart()
	msg['From'] = from_add
	msg['To'] = to_add
	msg['Subject'] = f'Motion detected on {cur_time}'
	Body = "Moving object displayed below"
	msg.attach(MIMEText(Body, 'plain'))

	filename = f'{cur_time}.jpg'
	image = open(os.path.join("objects",filename), "rb")

	p = MIMEBase('application','octet-stream')
	p.set_payload((image).read())

	encoders.encode_base64(p)

	p.add_header('Content-Disposition',"attachment; filename=%s" % filename)
	msg.attach(p)

	s = smtplib.SMTP('smtp.gmail.com', 587)
	#s = smtplib.SMTP('smtp.mail.yahoo.com',587)
	s.starttls()
	s.login(from_add, password)

	text = msg.as_string()
	s.sendmail(from_add, to_add, text)
	s.quit()


def Security_cam(cam=0, hold_time=5, cascades=[face_cascade,body_cascade], cascade_acc=1.3,
	announce_rec=False, show_camera=True, show_boxes=False, mail_notification=False):

	source = cv2.VideoCapture(cam, cv2.CAP_DSHOW)
	size = (int(source.get(3)),int(source.get(4)))

	detection = False
	timer_start = False
	#hold_time = 5 #wait time before stopping current recording

	while (source.isOpened()):
		_,frame = source.read()

		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		"""
		faces = face_cascade.detectMultiScale(gray, 1.3, 5)
		bodies = body_cascade.detectMultiScale(gray, 1.3, 5)
		"""
		ttl_objects = 0
		for cascade in cascades:
			objects = cascade.detectMultiScale(gray, cascade_acc, 10)
			ttl_objects += len(objects)

		if ttl_objects > 0:
			if detection:
				timer_start = False

			else:
				detection = True
				cur_time = dt.now().strftime("%b%d_%H-%M-%S")
				rec = cv2.VideoWriter(f'{cur_time}.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 10, size)
				#out = cv2.VideoWriter(f'{cur_time}.avi', cv2.VideoWriter_fourcc(*'MJPG'), 10, size)
				if announce_rec:
					print("Recording Started")

				if mail_notification==True:
					Mail_img()
				else:
					if not(os.path.exists("objects")):
						os.mkdir("objects")
					cur_time = dt.now().strftime("%b%d_%H-%M-%S")
					cv2.imwrite(os.path.join("objects",f'{cur_time}.jpg'),frame)

		elif detection:
			if timer_start:
				if time.time()-detect_stoptime >= hold_time:
					detection = False
					timer_start = False
					rec.release()
					if announce_rec:
						print("Recording Stopped")

			else:
				timer_start = True
				detect_stoptime = time.time()
				

		if detection:
			rec.write(frame)

		#To display boxes around faces
		if show_boxes and show_camera:
			for cascade in cascades:
				objects = cascade.detectMultiScale(gray, cascade_acc, 5)
				for (x,y,w,h) in objects:
					cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

		elif show_camera:
			cv2.imshow("Camera feed", frame)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cv2.destroyAllWindows() 
	source.release()
	rec.release()

Security_cam(announce_rec=True, mail_notification=True)
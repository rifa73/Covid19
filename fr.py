import Db
import base64
import io
from PIL import Image
import cv2 
import mtcnn
import numpy as np
import tensorflow as tf
import FaceRecognition
import mtcnn

detector = mtcnn.MTCNN()
database = Db.Db()
employeeIds, employeeEmbeddings = database.getembeddings()
face_recog = FaceRecognition.face_recognition(employeeIds, employeeEmbeddings)
i = 0
vid = cv2.VideoCapture(0)

while(True):
    ret, frame = vid.read()
    if i%30==0:
        faces = detector.detect_faces(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        for result in faces:
            x, y, w, h = result['box']
            face = frame[y:y+h,x:x+w]
            eid = face_recog.recognize(face)
            name, email = database.getdetails(eid)
            print(name, email)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    i = i + 1

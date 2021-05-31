import cv2 
import mtcnn
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from PIL import Image
from skimage import transform
import numpy as np
import math
from crowdandSocialDistancing import crowd_detection
from DBThreads import Threads
import datetime
import FaceRecognition
from tensorflow.keras import backend as K
from EmailNotification import email_notification
import logging

logging.basicConfig(level=logging.INFO)

class endpoint:

    def __init__(self):
        self.detector = mtcnn.MTCNN()
        self.model = tf.keras.models.load_model(r'D:\FYP practice and stuff\MaskDetection.h5', custom_objects={"f1_m": self.f1_m, "precision_m": self.precision_m, "recall_m": self.recall_m})
        self.thread = Threads()
        self.place = 'my house'
    
    def recall_m(self, y_true, y_pred):
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        recall = true_positives / (possible_positives + K.epsilon())
        return recall

    def precision_m(self, y_true, y_pred):
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        precision = true_positives / (predicted_positives + K.epsilon())
        return precision

    def f1_m(self, y_true, y_pred):
        precision = self.precision_m(y_true, y_pred)
        recall = self.recall_m(y_true, y_pred)
        return 2*((precision*recall)/(precision+recall+K.epsilon()))

    def maskDetection(self,faces,frame,ct):
        try:
            green = (0, 255, 0)
            red = (0,0,255) 
            thickness = 3
        
            for result in faces:
                x, y, w, h = result['box']
                face = frame[y:y+h,x:x+w]

                np_image = np.array(face).astype('float32')/255
                np_image = transform.resize(np_image, (150, 150, 3))
                np_image = cv2.cvtColor(np_image, cv2.COLOR_BGR2RGB)
                np_image = np.expand_dims(np_image, axis=0)
                scores = self.model.predict_classes(np_image)
            
                if scores == 1:
                    self.thread.mask_q.put((frame, self.place, ct))
                    logging.info('Mask violation Detected')
                    frame = cv2.rectangle(frame, (x,y), (x+w, y+h), red, thickness)
                elif scores == 0:
                    frame = cv2.rectangle(frame, (x,y), (x+w, y+h), green, thickness)
        except:
            pass
             

    def crowdDetection(self,faces):
        crowd_obj=crowd_detection(3)
        check_crowd, Status=crowd_obj.detect(faces)
        return (check_crowd, Status)

    def faceDetection(self,frame):
        faces = []
        faces = self.detector.detect_faces(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) 
        return faces

   
    def doWork(self):
        en = email_notification()
        vid = cv2.VideoCapture(0)
        self.thread.t1.start()
        self.thread.t2.start()
        
        i=0

        while(True):
            ret, frame = vid.read()
            if type(frame) == None:
                logging.info('Couldnt read frame')
                continue
            i = i + 1
            ct = datetime.datetime.now()
            if i%30 != 0:
                continue # processing 1 in 30th frame only.
            faces=self.faceDetection(frame)
            if len(faces) > 0:
                if i%45 == 0:
                    check_crowd, violation_type =self.crowdDetection(faces)
                    if(check_crowd==True):
                        self.thread.crowd_q.put((frame, self.place, ct, violation_type))
                        logging.info('Crowd violation detected')
                        en.sendEmail('None','None',ct, 'Crowd', 'Gate2')
                
                self.maskDetection(faces,frame,ct)
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("call break")
                break
        print("release n destroy")
        if cv2.waitKey(1) & 0xFF == ord('q'):
                print("call break")
                vid.release()
                cv2.destroyAllWindows()

        self.thread.crowd_q.put((None, None, None,None))
        self.thread.mask_q.put((None, None, None))
        vid.release()
        cv2.destroyAllWindows()
        self.thread.t1.join()
        self.thread.t2.join()




endpoint_obj=endpoint()
endpoint_obj.doWork()
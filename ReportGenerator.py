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
import EmailNotification
import uuid
from bson.objectid import ObjectId
import logging

logging.basicConfig(level=logging.INFO)

class ReportGenerator:

    def __init__(self):
        self.keys = []
        self.detector = mtcnn.MTCNN()
        self.database = Db.Db()
        self.employeeIds, self.employeeEmbeddings, self.unknownIds, self.unknownEmbeddings, self.unknownTimestamp = self.database.getInformation()
        self.violations = self.database.getMaskViolations()
        self.face_recog = FaceRecognition.face_recognition(self.employeeIds, self.employeeEmbeddings, self.unknownIds, self.unknownEmbeddings, self.unknownTimestamp)
        self.EN = EmailNotification.email_notification()
        self.unknownId = self.database.getMax()


    def stringToRGB(self,base64_string):
        imgdata = base64.b64decode(str(base64_string))
        image = Image.open(io.BytesIO(imgdata))
        return cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)


    def updateViolations(self,arr):
        for x in arr:
            self.violations.append(x)


    def timeDifference(self, timestamp, violationTimestamp):
        if timestamp > violationTimestamp:
            td = timestamp - violationTimestamp
        else:
            td = violationTimestamp - timestamp
        td_mins = int(td.total_seconds() / 60)
        logging.info('Time difference: '+ str(td_mins))
        return td_mins
    

    def checkUnknown(self,face,violationTime):
        
        logging.info('Person not identified')
        uid, timestamp, embedding = self.face_recog.recognizeUnknown(face)
        
        if uid == -1:
            logging.info('First entry')
            wasFaceProcessed = self.database.populateViolations(self.unknownId, face, violationTime, 'Gate1')
            if wasFaceProcessed:
                self.database.populateUnknown(self.unknownId, face, embedding, 'Gate1', violationTime)
                self.face_recog.UpdateUnknown()
                self.unknownId = self.unknownId + 1
                temp = self.database.UpdateMaskViolations(self.violations)
                self.updateViolations(temp)
        else:
            td = self.timeDifference(timestamp, violationTime)
            
            if td > 3:
                self.database.updateTimestamp(uid, violationTime)
                wasFaceProcessed = self.database.populateViolations(uid, face, violationTime, 'Gate1')
                if wasFaceProcessed:
                    temp = self.database.UpdateMaskViolations(self.violations)
                    self.updateViolations(temp)

    
    def checkEmployee(self, eid, face, violationTime):
        timestamp = self.database.getLatestViolation(eid)
        logging.info("time of last violation: " + str(timestamp))
        logging.info("time of current violation: " + str(violationTime))
        
        #Pehli baar aaya hai
        if timestamp == None:
            name, email = self.database.getDetails(eid)
            logging.info(name + ' ' + email)
            self.EN.sendEmail(name, email, violationTime, 'Mask', None)
            self.database.populateViolations(eid, face, violationTime, 'university')
            temp = self.database.UpdateMaskViolations(self.violations)
            self.updateViolations(temp)
        else:
            td = self.timeDifference(timestamp, violationTime)
            if td > 3:
                name, email = self.database.getDetails(eid)
                logging.info(name + ' ' + email)
                self.EN.sendEmail(name, email, violationTime, 'Mask', None)
                self.database.populateViolations(eid, face, violationTime, 'entrance')
                temp = self.database.UpdateMaskViolations(self.violations)
                self.updateViolations(temp)


    def generate(self):
        for viol in self.violations:
            image = self.stringToRGB(viol['image'])
            faces = self.detector.detect_faces(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            for result in faces:
                x, y, w, h = result['box']
                face = image[y:y+h,x:x+w]
                eid = self.face_recog.recognizeEmployee(face)
                if eid != -1:
                    self.checkEmployee(eid, face, viol['ToV'])
                else:
                    self.checkUnknown(face, viol['ToV'])
            self.keys.append(str(viol['_id']))
        self.database.updateNoMask(self.keys)



rg = ReportGenerator()
rg.generate()
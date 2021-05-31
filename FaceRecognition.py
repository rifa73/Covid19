import mtcnn
import cv2
import base64
from bson.objectid import ObjectId
import io
import numpy as np
from PIL import Image
from numpy import asarray, expand_dims
from scipy.spatial.distance import cosine
from keras_vggface.utils import preprocess_input
from numpy import asarray, expand_dims
import tensorflow as tf
from json import dumps, loads
import Db
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
from keras_vggface.utils import decode_predictions
import logging

logging.basicConfig(level=logging.INFO)

class face_recognition:
    def __init__(self, employeeIds, employeeEmbeddings, unknownIds, unknownEmbeddings, unknownTimestamp):
        self.database = Db.Db()
        self.employeeIds = employeeIds
        self.employeeEmbeddings = employeeEmbeddings
        self.unknownIds = unknownIds
        self.unknownEmbeddings = unknownEmbeddings
        self.unknownTimestamp = unknownTimestamp
        self.embedder = VGGFace(model='resnet50', include_top=False, input_shape=(224, 224, 3), pooling='avg')
        

    def getEmbedding(self, frame,  required_size=(224, 224)):
        image = Image.fromarray(frame)
        image = image.resize(required_size)
        face_array = asarray(image)
        samples = asarray(face_array, 'float32')
        samples = expand_dims(samples, axis=0)
        samples = preprocess_input(samples, version=2)
        yhat = self.embedder.predict(samples)
        return yhat


    def isMatch(self, knownEmbedding, candidateEmbedding, thresh=0.35):
        score = cosine(knownEmbedding, candidateEmbedding)
        if score <= thresh:
            return True
        else:
            return False


    def recognizeEmployee(self,face):
        eid = -1
        try:
            embedding = self.getEmbedding(face)
            for i in range(0,len(self.employeeEmbeddings)):
                match = self.isMatch(embedding, self.employeeEmbeddings[i])
                if (match == True):
                    eid = self.employeeIds[i]
                    return eid
            return -1
        except:
            return -1


    def recognizeUnknown(self,face):
        eid = -1
        try:
            embedding = self.getEmbedding(face)
            for i in range(0,len(self.unknownEmbeddings)):
                match = self.isMatch(embedding, self.unknownEmbeddings[i])
                if (match == True):
                    eid = self.unknownIds[i]
                    timestamp = self.unknownTimestamp[i]
                    logging.info(eid)
                    return (eid, timestamp, embedding)
            return (-1, -1, embedding)
        except:
            return (-1,-1,None)
    

    def UpdateUnknown(self):
        self.unknownIds, self.unknownEmbeddings, self.unknownTimestamp = self.database.getUnknownInfo()
        logging.info('Information about unknown updated')

    def UpdateEmployee(self):
        self.employeeIds, self.employeeEmbeddings = self.database.getEmployeeInfo()
import base64
from pymongo import MongoClient
import cv2
import numpy as np
from json import loads
from bson.objectid import ObjectId
import logging

logging.basicConfig(level=logging.INFO)

class Db:

    
    def __init__(self):
        self.client = MongoClient("mongodb+srv://<username>:<password>@cluster0.bpkkq.mongodb.net/EnforcementSystem?retryWrites=true&w=majority", maxPoolSize=50)
        self.database = self.client['Zolar']
        self.nomask = self.database['NoMask']
        self.employee = self.database['Employee']
        self.crowddetected = self.database['SocialViolation']
        self.violation = self.database['ViolationLog']
        self.unknown = self.database['UnknownPeople']


    def populateMaskViolation(self, np_image, timestamp, place, processed = False):
        retval, buffer = cv2.imencode('.jpg', np_image)
        b64_string = (base64.b64encode(buffer)).decode()
        self.nomask.insert_one({'ToV': timestamp, 'image': b64_string, 'place': place,'processed': processed})
        logging.info('Mask Detection table populated')


    def populateCrowdViolation(self, frame, crowd_timestamp, place, violation_type, processed= False):
        retval, buffer = cv2.imencode('.jpg', frame)
        b64_string = (base64.b64encode(buffer)).decode()
        self.crowddetected.insert_one({'ToV': crowd_timestamp, 'Crowd': b64_string, 'place': place,'Type': violation_type,  'processed': processed})
        logging.info('Crowd Detection table populated')
    

    def populateUnknown(self, _id, frame, embedding, place, timestamp):
        dims = frame.shape
        if dims[0] >=100 and dims[1] >= 100:
            retval, buffer = cv2.imencode('.jpg', frame)
            b64_string = (base64.b64encode(buffer)).decode()
            embedding = base64.b64encode(embedding)
            self.unknown.insert_one({'uid': _id, 'image': b64_string, 'Embeddings': embedding, 'place': place, 'Timestamp': timestamp})
            logging.info('Unknown table populated')


    def getInformation(self):
        test = self.employee.find({}, { '_id' : 0, 'Emp_id' : 1, 'Embeddings' : 1})
        test2 = self.unknown.find({}, { '_id' : 0, 'uid' : 1,  'Embeddings' : 1, 'Timestamp': 1})
        unknownIds = []
        unknownEmbeddings = []
        unknownTimestamp = []
        employeeIds = []
        employeeEmbeddings = []

        for x in test:
            d = base64.decodebytes(x['Embeddings'])
            q = np.frombuffer(d, dtype=np.float32)
            employeeEmbeddings.append(q)
            employeeIds.append(x['Emp_id'])
        
        for x in test2:
            d = base64.decodebytes(x['Embeddings'])
            q = np.frombuffer(d, dtype=np.float32)
            unknownEmbeddings.append(q)
            unknownIds.append(str(x['uid']))
            unknownTimestamp.append(x['Timestamp'])
        return (employeeIds, employeeEmbeddings, unknownIds, unknownEmbeddings, unknownTimestamp)

    
    def getUnknownInfo(self):
        test2 = self.unknown.find({}, { '_id' : 0, 'uid' : 1,  'Embeddings' : 1, 'Timestamp': 1})
        unknownIds = []
        unknownEmbeddings = []
        unknownTimestamp = []

        for x in test2:
            d = base64.decodebytes(x['Embeddings'])
            q = np.frombuffer(d, dtype=np.float32)
            unknownEmbeddings.append(q)
            unknownIds.append(str(x['uid']))
            unknownTimestamp.append(x['Timestamp'])
        return (unknownIds, unknownEmbeddings, unknownTimestamp)


    def getDetails(self, id):
        if id == -1:
            return (None, None)
        details = self.employee.find_one({'Emp_id' : id},{'_id': 0, 'Name': 1, 'Email_address': 1})
        return (details['Name'], details['Email_address'])
    

    def getMaskViolations(self):
        maskViolations = []
        temp = self.nomask.find({'processed': False})
        for x in temp:
            maskViolations.append(x)
        return maskViolations


    def updateNoMask(self, keys):
        if len(keys) != 0:
            for x in keys:
                self.nomask.update_one({'_id' : ObjectId(x)}, {'$set':{'processed': True}})


    def getViolations(self):
        violations = []
        violations_cursor = self.violation.find({})
        for x in violations_cursor:
            violations.append(x)
        return violations
    

    def populateViolations(self, eid, picture, timestamp, place):
        dims = picture.shape
        if dims[0] >=100 and dims[1] >= 100:
            retval, buffer = cv2.imencode('.jpg', picture)
            b64_string = (base64.b64encode(buffer)).decode()
            self.violation.insert_one({'eid': eid, 'image': b64_string , 'ToV': timestamp, 'place': place})
            logging.info('Violations table populated')
            return True
        else:
            logging.info('Face not entered')
            return False
            
    
    def getLatestViolation(self, eid):
        latest = []
        temp = self.violation.find({'eid': eid}).sort('ToV',-1).limit(1)
        temp = list(temp)
        if len(temp) == 0:
            return None
        else:
            for x in temp:
                latest.append(x)
            return latest[0]['ToV']


    def updateTimestamp(self, uid, timestamp):
        self.unknown.update_one({'uid': uid}, {'$set': {'Timestamp': timestamp}})


    def getMax(self):
        empLatest = []
        unknownLatest = []
        temp = self.employee.find({}).sort('Emp_id',-1).limit(1)
        temp1 = self.unknown.find({}).sort('uid',-1).limit(1)
        temp = list(temp)
        temp1 = list(temp1)
        if len(temp1) == 0 and len(temp) == 0:
            return None
        else:
            for x in temp:
                empLatest.append(x)
            for y in temp1:
                unknownLatest.append(y)
            if len(temp1) != 0:
                return (empLatest[0]['Emp_id'] + unknownLatest[0]['uid'] + 1)
            else:
                return (empLatest[0]['Emp_id'] + 1)


    def UpdateMaskViolations(self,arr):
        y = []
        maximum = arr[0]['ToV']
        for x in arr:
            if x['ToV'] > maximum:
                maximum = x['ToV']

        violations = self.nomask.find({'Tov': {'$gte': maximum }})
        for x in violations:
            y.append(x)
        return y

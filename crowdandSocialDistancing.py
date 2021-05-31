import math


class crowd_detection:

    def __init__(self,threshold_value):
        self.threshold_value=threshold_value

    def calculateDistance(self,x1,y1,x2,y2):

     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

     return dist

    def detect(self,faces):
        return_value = ''
        if(len(faces)>self.threshold_value):
            return_value += 'Crowd '
        x_coor=[]
        y_coor=[]
        h_coor=[]
        for result in faces:
            x, y, w, h = result['box']
            x_coor.append(x)
            y_coor.append(y)
            h_coor.append(h)

        maxHeight = max(h_coor)
        sdv = ''
        for k in range(0,len(faces)):

            for j in range(k,len(faces)):
                if(k!=j):
                    dist=self.calculateDistance(x_coor[k],y_coor[k],x_coor[j],y_coor[j])
                    if(dist<(maxHeight*2)):
                        sdv = 'social distancing'
        return_value += sdv
        x_coor=[]
        y_coor=[]
        return (len(return_value)!=0, return_value)
                        
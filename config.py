import math

class Config:
    def __init__(self, nPhotos):
        self.nPhotos = nPhotos
    def setData(self, data):
        self.data = data

    def getOrientation(self, photoIdx):
        return self.data[photoIdx][0]

    def getTags(self, photoIdx):
        return self.data[photoIdx][2:]

    def getNumSlides(self):
        nSlides = 0
        for photo in self.data:
            if photo[0] == 'H':
                nSlides += 1
            else:
                nSlides += 0.5
        
        return math.floor(nSlides)
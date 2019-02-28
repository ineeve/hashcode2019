class Config:
    def __init__(self, nPhotos):
        self.nPhotos = nPhotos
    def setData(self, data):
        self.data = data

    def getOrientation(self, photoIdx):
        return self.data[photoIdx][0]

    def getTags(self, photoIdx):
        return self.data[photoIdx][2:]
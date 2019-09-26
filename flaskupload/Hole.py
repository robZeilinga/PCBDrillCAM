import math
from collections import defaultdict

class Hole:

    hole_index = defaultdict(list)

    def __init__(self, holeNum, point, toolNum):
        self.toolNum = toolNum
        self.filePoint = point
        self.rotationAngle = 0
        self.isHoleZero = False
        self.isHole2 = False 
        self.holeZero = None
        self.flippedY = None
        self.zeroedAndFlippedPoint = [-999.999, -999.999]
        self.rotatedPoint = None
        self.holeNumber = holeNum
        Hole.hole_index[holeNum].append(self)
    
    @classmethod
    def find_by_number(cls, num):
        return Hole.hole_index.get(num)

    def rotate(self):
        if self.holeZero == None:
            # throw Exception
            raise Exception("'Hole Zero not Set, Cannot Rotate")
        rotationAngle = self.rotationAngle
        # get angle from Hole Zero 
        
        zX, zY  = self.zeroedAndFlippedPoint

        currentAngle = math.atan2(zY, zX)
        angleinRadsToRotate = math.radians(rotationAngle) + currentAngle
        dist = math.sqrt((zX)**2 + (zY)**2)
        self.rotatedX = self._rotate(angleinRadsToRotate)


    def _rotate(self, angle):
        """
        Rotate a point counterclockwise by a given angle around a given origin.

        The angle should be given in radians.
        """
        px, py = self.zeroedAndFlippedPoint
        qx = math.cos(angle) * (px) - math.sin(angle) * (py)
        qy = math.sin(angle) * (px) + math.cos(angle) * (py)
        self.rotatedPoint = qx,qy
 
        
    def translateAndFlipHole(self, minY, maxY, minX):
        # move to X = 0 axis
        
        self.zeroedAndFlippedPoint[0] = self.filePoint[0] - minX
        # do the same for y  (minY )

        
        translatedY = self.filePoint[1] - (minY)
        # flip the Y point
        # first move the maxY to Y=0 axis 
        maxTranslatedY = maxY - minY
        self.zeroedAndFlippedPoint[1] = maxTranslatedY - translatedY

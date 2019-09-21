import math
import matplotlib.pyplot as plt
from collections import defaultdict
import mplcursors


h0Picked = False
h2Picked = False
h0Index = -1
h2Index = -1

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
        translatedY = self.filePoint[1] - minY
        # flip the Y point
        # first move the maxY to Y=0 axis 
        maxTranslatedY = maxY - minY
        self.zeroedAndFlippedPoint[1] = maxTranslatedY - translatedY

def switch_tool(argument):
    switcher = {
        1: "black",
        2: "green",
        3: "blue",
        4: "yellow",
        5: "red",
        6: "pink",
        7: "orange",
        8: "purple",
        9: "cyan",
        10: "red",
        11: "blue",
        12: "green"
    }
    return switcher.get(argument)


def rotateX(px, py, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    radAngle = math.radians(angle)
    
    qx = math.cos(angle) * (px) - math.sin(angle) * (py)
    return qx

def rotateY(px, py, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    qy = math.sin(angle) * (px) + math.cos(angle) * (py)
    return qy


def onpick(event):
    
    font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 16,
        }


    thisline = event.artist
    print(thisline)
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()
    print(xdata)
    ind = event.ind
    points = tuple(zip(xdata[ind], ydata[ind]))
    global h0Picked
    global h2Picked
    global h0Index
    global h2Index

    if h0Picked == False and h2Picked == False:
        print('Hole zero index:', thisline._label)
        h0Index = int(thisline._label)
        hh = Hole.find_by_number(h0Index)
        hh[0].isHoleZero = True
        h0Picked = True
        
        plt.title('PCB Driller\n Please Select : \n Hole zero : %d \n Hole 2 : %d'% (h0Index, h2Index), fontdict=font)
        plt.draw()
    elif h0Picked == True and h2Picked == False:
        
        print("hole 2 index:", thisline._label)
        h2Index = int(thisline._label)
        hh = Hole.find_by_number(h2Index)
        hh[0].isHole2 = True
        h2Picked == True
        plt.title('PCB Driller\n Please Select : \n Hole zero : %d \n Hole 2 : %d'% (h0Index, h2Index), fontdict=font)
        plt.close()


def main():

    font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 16,
        }


    px = -100.0
    py = -100.0
    global h0Picked
    h0Picked = False
    global h2Picked 
    h2Picked = False
    global h0Index
    global h2Index
    h0Index = -1
    h2Index = -1
    currentTool = 0
    toolsDict = dict()
    holes = []

    f= open("pic_programmer.drl","r")
    percFound = False
    cFound = False
    holeNum = 0
    holePrefix = "H"
    fl =f.readlines()
    for x in fl:
        cFound = "C" in x
        if x[0] == '%':
            percFound = True

        if x[0] == "T" and percFound == False and cFound == True:
            # Tool Found
            parts = x.split("C")
            #print("tool found, TOOL NUMBER: " + parts[0][1:5].strip() + " Size: " + parts[1])
            toolsDict[parts[0][1:5].strip()] = parts[1]
        if x[0] == "T" and percFound == True:
            currentTool = int(x[1:5].strip())
            if currentTool != 0:
                pass

                
        if x.strip().upper() == "M30":
            #done
            pass
        if x.startswith("X") and currentTool != 0:
            # we have a hole 
            
            parts = x.split("Y")
            xpart = float(parts[0][1:7])/1000
            ypart = float(parts[1])/1000
            filePoint = xpart, ypart
            holeNum = holeNum + 1
            holes.append(Hole(holeNum, filePoint, currentTool))
            
        #else:
            #print(x)
    for t, s in toolsDict.items():
        print("Tool #: " + t + " Size: " + s)

    currentTool = -1
    for h in holes:
        if h.toolNum != currentTool:
            currentTool = h.toolNum

    
    holeZero = Hole.find_by_number(int(holeNum))
    minX = 999.999
    minY = 999.999  
    maxY = -999.999
    for h in holes:
        if h.holeNumber == int(holeNum):
            h.isHoleZero = True
        else:
            h.holeZero = holeZero[0]
            if h.filePoint[0] < minX:
                minX = h.filePoint[0]
            if h.filePoint[1] < minY:
                minY = h.filePoint[1]
            if h.filePoint[1] > maxY:
                maxY = h.filePoint[1]
    
    f = open("demofile2.txt", "w")
    cnt = 0
    fig = plt.figure(figsize=(10,8))
    fig.canvas.mpl_connect('pick_event', onpick)

    plt.title('PCB Driller\n Please Select : \n Hole zero : unpicked \n Hole 2 : unpicked', fontdict=font)
    for h in holes:
        h.translateAndFlipHole(minY, maxY, minX )
        f.write("%3d,%3.3f,%3.3f,%d,%s"% (h.holeNumber, h.zeroedAndFlippedPoint[0], h.zeroedAndFlippedPoint[1], h.toolNum, toolsDict[str(h.toolNum)] ))
        print("#%d Tool:%d PlotX: %3.3f PlotY: %3.3f"% (cnt, h.toolNum, h.zeroedAndFlippedPoint[0], h.zeroedAndFlippedPoint[1]))
        if(cnt < 260):
            px = h.zeroedAndFlippedPoint[0]
            py = h.zeroedAndFlippedPoint[1]
            plt.plot(px,py,color=switch_tool(h.toolNum),markersize = h.toolNum, marker = 'o', label=cnt, picker=5)
            cnt=cnt+1
    f.close()

    plt.show()
    import math
    #getAngle between holes
    hh = Hole.find_by_number(h2Index)
    radFileAngle = math.atan2(hh[0].zeroedAndFlippedPoint[1], hh[0].zeroedAndFlippedPoint[0])
    fileDegrees = math.degrees(radFileAngle)
    print("radAngle %3.2f"% (radFileAngle))
    print("degrees %3.2f"% (fileDegrees) )
    print("Step 1 of 10")
    print("-----------")
    dummy = input("Home CNC, and Zero all [ G92 X0 Y0 Z0], press enter when done")
    print("Step 2 of 10")
    print("-----------")
    SafeZHeight = float(input("Enter Safe Z height "))
    print("Step 3 of 10")
    print("-----------")
    DrillDepth = float(input("Enter DrillDepth"))
    print("Step 4 of 10")
    print("-----------")
    dummy = input("Move CNC (at Safe Z Height), to locate Hole Zero on the PCB. press enter when ready")
    print("Step 5 of 10")
    print("-----------")
    dummy = input("Zero the CNC X & Y Value [G92 X0 Y0] Do NOT zero Z, press enter when ready")
    print("Step 6 of 10")
    print("-----------")
    h2X = float(input("Locate Hole 2 and Enter the X Value "))
    print("Step 7 of 10")
    print("-----------")
    h2Y = float(input("Enter the Y value of Hole 2"))
    print("Step 8 of 10")
    print("-----------")
    CamX = float(input("Enter the X offset of the camera"))
    print("Step 9 of 10")
    print("-----------")
    CamY = float(input("Enter the Y offset of the camera"))
    print("Step 10 of 10")
    print("-----------")
    FR = int(input("Enter the Feed Rate "))

    # calculate angle of PCB 
    radPCBAngle = math.atan2(float(h2Y),float(h2X))
    pcbDegrees = math.degrees(radPCBAngle)
    rotAngle = radFileAngle - radPCBAngle

    
    for h in holes:
        if h.isHoleZero == False:
            h.rotationAngle = rotAngle
            h.rotate()

    # rotate holes 

    print("Generating .......")
    
    import math
    pcbDist = ((float(h2X))**2 + (float(h2Y))**2)**0.5
    print("PCB Dist = " + str(pcbDist))

    
    print("PCB Angle (in rads) = " + str(radPCBAngle))
    print("PCB Angle in Degrees = " + str(math.degrees(radPCBAngle)))

    #scale = dist/pcbDist
    #print("Scale : %3.3f"% (scale))
    
    print("Result Angle [rads] : %3.3f"% rotAngle)
    print("PCB Rotation : %3.3f"% (math.degrees(rotAngle)))

    print("(CNC FILE GENERATED BY PCB DRILLER V1")
    print("()")
    print("G20 (mm)")
    print("G90 (absolute)")
    print("")
    print("(Hole Zero)")
    print("G0 X0 Y0 Z%3.3f F%d"% (SafeZHeight, FR))
    print("G0 Z%3.3f F%d"% (SafeZHeight+DrillDepth, FR))
    print("G0 Z%3.3f F%d"% (SafeZHeight, FR))
    for h in holes:
        if h.isHoleZero == False:
            h.rotationAngle = rotAngle
            h.rotate()
            print("G0 X%3.3f Y%3.3f F%d"% (h.rotatedPoint[0], h.rotatedPoint[1], FR) )
            print("G0 Z%3.3f F%d"% (SafeZHeight+DrillDepth, FR))
            print("G0 Z%3.3f F%d"% (SafeZHeight, FR))

    print("G0 X0 Y0 F%d"% (FR))

    print("Finished")



if __name__== "__main__":
  main()






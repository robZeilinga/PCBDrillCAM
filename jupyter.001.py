#!/usr/bin/env python
# coding: utf-8

# In[73]:

from IPython import get_ipython
import pandas as pd
df = pd.read_csv("/Users/robzeilinga/Desktop/_REPO/Python/ReadDrillFile/demofile2.txt", sep=",", index_col=False, names=['id','x','y','t','s'])
#df.tail(8)
import matplotlib.pyplot as plt
from IPython import get_ipython
ipy = get_ipython()
if ipy is not None:
    ipy.run_line_magic('matplotlib', 'inline')#get_ipython().run_line_magic('matplotlib', 'inline')
fig= plt.figure(figsize=(16,9))
plt.scatter(df.x,df.y,s=df.s*50, c=df.t, cmap = "nipy_spectral")
for i, txt in enumerate(df.id):
    #if i == 244:
    plt.annotate(i, ((df.x[i]+0.9), (df.y[i]+0.9)))


# In[75]:


h0 = input("enter hole 0 : ")
print(h0)
h2 = input("enter hole 2 : ")
print(h2)


# In[79]:


fig= plt.figure(figsize=(14,9)) 
plt.scatter(df.x,df.y,s=df.s*50, c=df.t, cmap = "nipy_spectral")


for i,txt in enumerate(df.id): 
    if i == int(h0):
        #print("in here")
        h0x = df.x[i]
        h0y = df.y[i]
        print("H0 [" + str(h0x) + ", " + str(h0y) + "]")
        plt.annotate('H0', ((df.x[i]+0.9), (df.y[i]+0.9)))
    if i == int(h2):
        h2x = df.x[i]
        h2y = df.y[i]
        print("H2 [" + str(h2x) + ", " + str(h2y) + "]")
        plt.annotate('H2', ((df.x[i]+0.9), (df.y[i]+0.9)))

import math 
dist = ((h2x-h0x)**2 + (h2y-h0y)**2)**0.5 
print("dist = " + str(dist)) 
deltaX = h2x - h0x 
deltaY = h2y - h0y 
print("deltaX ; " + str(deltaX)) 
print("deltaY ; " + str(deltaY))

angleOriginal = math.atan2(deltaY,deltaX) 
print("angleOriginal (in rads) = " + str(angleOriginal)) 
angleDegrees = math.degrees(angleOriginal) 
print("Degrees = " + str(angleDegrees))


# In[80]:


import math
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
    radAngle = math.radians(angle)
    
    qy = math.sin(angle) * (px) + math.cos(angle) * (py)
    return qy


# In[81]:


fig= plt.figure(figsize=(15,15))
newRot = 45.0
#newRot = math.radians(rot)
print("newRot = " + str(newRot))
plt.scatter(rotateX(df.x, df.y, newRot),rotateY(df.x, df.y, newRot),s=df.s*50, c=df.t, cmap = "nipy_spectral")



# In[ ]:


print("==================================")
print("=            CNC STEPS           =")
print("=            ---------           =")
print("=                                =")
print("=Step 1: Get Camera Offset       =")
print("=Step 2: determine safe Z height =")
print("=Step 3: move Camera to Hole 0   =")
print("=Step 4: Zero X & Y  G92 x0 y0   =")
print("=Step 5: move Camera to Hole 2   =")
print("=Step 6: make a note of coords   =")
print("=Step 7: Enter values below      =")
print("==================================")

CamOffSetX = float(input("Enter camera X offset : "))
CamOffSetY = float(input("Enter camera Y offset : "))
SafeZ = float(input("Enter Safe Z Height : "))
try:
    DrillDepth = float(input("Enter depth of Drill [default = 5] : "))
except ValueError:
    DrillDepth = 5.0
hole2X = float(input("Enter Hole 2 X Value : "))
hole2Y = float(input("Enter Hole 2 Y Value : "))

import math
pcbDist = ((hole2X)**2 + (hole2Y)**2)**0.5
print("PCB Dist = " + str(pcbDist))

pcbAngle = math.atan2(hole2Y,hole2X)
print("PCB Angle (in rads) = " + str(pcbAngle))
pcbAngleDegrees = math.degrees(pcbAngle)
print("PCB Angle in Degrees = " + str(pcbAngleDegrees))

scale = dist/pcbDist
print("Scale : %3.3f"% (scale))

rotAngle = angleDegrees - pcbAngle
print("PCB Rotation : %3.3f"% (rotAngle))


# In[69]:


for i,txt in enumerate(df.id):
    print("G0 Z80")
    print("G0 Z70")
    newX = rotateX(df.x[i], df.y[i], rotAngle)
    newY = rotateY(df.x[i], df.y[i], rotAngle)
    print("G0 X%3.3f Y%3.3f"% (newX, newY))


# In[ ]:





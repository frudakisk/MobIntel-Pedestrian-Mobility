#from Functionality import RSSIToDistanceLib
import sys, numpy
sys.path.append("pythonFiles")

from Functionality import RSSIToDistanceLib as rssiLib

#this print statement should return an integer that represents
#a distance in meters
d = rssiLib.rssiToDistance(-50)
if(type(d) != numpy.float64):
    raise Exception("Return type not a float")
else:
    print(d)

d = rssiLib.rssiToDistanceV2(-61)
if(type(d) != numpy.float64):
    raise Exception("Return type not a float")
else:
    print(d)


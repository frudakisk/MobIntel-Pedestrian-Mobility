from math import pi, cos
from geopy import distance

def adjustedLongitude(t, x):
  """t is the tuple of (lat,long) of reference location.
  x is the distance, in meters, from the reference point.
  If x is positive, this distance is eastward.
  If x is negative, this distance is westward.
  Returns a new (lat,long) that is adjusted by x meters"""
  rEarth = 6371000.0
  newLongitude = t[1] + (x / rEarth) * (180/pi) / cos(t[0] * pi/180)
  return (t[0], newLongitude)

def adjustedLatitude(t, y):
  """t is the tuple of (lat,long) of reference location.
  y is the distance, in meters, from the reference point.
  If y is positive, this distance is northward.
  If y is negative, this distance is southward.
  Returns a new (lat,long) that is adjusted by y meters"""
  rEarth = 6371000.0
  newLatitude  = t[0]  + (y / rEarth) * (180 / pi)
  return (newLatitude, t[1])
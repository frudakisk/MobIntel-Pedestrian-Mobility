import math

def freeSpacePathLossLinear(distance):
  """
  distance: distance in meters used to calculate ideal rssi value
  returns: ideal rssi value as a negative integer
  Description: This function returns the idea rssi using the free space path loss 
  linear model
  """
  transmitPower = 32.15
  tGain = pow(10, 5/10) #formula that converts 5 dBi to linear scale. https://shopdelta.eu/dbi-power-gain-of-isotropic-antenna_l2_aid836.html
  rGain = tGain # they are equivalent, in theory
  wavelength = (3 * pow(10, 8)) / (2.4 * pow(10, 9))
  return (transmitPower * tGain * rGain * pow((wavelength / (4 * 3.1415 * distance)), 2)) #equation 3


def freeSpacePathLossdB(distance):
  """
  distance: distance in meters used to calculate the ideal rssi value
  returns: returns idea rssi value in dbs which is represented as a negative float
  Description: This function is used to help pathLossExponent calculate its ideal 
  rssi value
  """
  transmitPower = 30 #this in dBm
  tGain = 2.85 #dBi to dB = dBi - 2.15
  rGain = tGain
  wavelength = (3 * pow(10, 8)) / (2.4 * pow(10, 9))
  pathLoss = 20 * math.log(((4 * 3.1415 * distance) / wavelength),10)
  return (transmitPower + tGain + rGain - pathLoss) #equation 4 in chapter 3


def pathLossExponent(distance):
  """
  distance: distance in meters used to calculate the ideal rssi value
  returns: ideal rssi value as a negative float
  Description: other two are struggling (freespacePathLossdb/Linear), so this 
  function is a better version of the two"""
  Friis = (freeSpacePathLossdB(0.89))
  #print("Friis is:", Friis)
  #print("Second term is:", (10 * 3) * math.log((distance / 0.89),10))
  return (Friis - (10 * 3) * math.log((distance / 0.89),10)) #path loss exponent is 3, should be between 2.7 - 3.5. Based on https://core.ac.uk/download/pdf/160645255.pdf
"""3.558 is d0 in equation (5) & (6) under 3.1. It is the "edge of near and far fields" of the antenna of the transmitter.
it is calculated based on an equation for near field region, defined as < 2(D^2) / wavelength, where D is the length of antenna.
antenna length is assumed to be 6 inches for now. """
#print("Path Loss Exponent Model:", pathLossExponent(94.5))


def FSPL(distance):
  """
  distance: distance in meters used to calculate the ideal rssi value
  returns: ideal rssi value
  Description: based on 
  https://www.pasternack.com/t-calculator-fspl.aspx?utm_campaign=Power_Combiners&keyword=&gclid=CjwKCAjwqZSlBhBwEiwAfoZUIC8PAydtbR9-tlF6zMTyv6Ei-CCCDZD86EJshD0cqsX4GtGsMiCA2xoCUGkQAvD_BwE
  """
  d = 20 * math.log(distance, 10)
  f = 20 * math.log((2.4 * pow(10, 9)), 10)
  c = 20 * math.log((4 * 3.1415) / (3 * pow(10, 8)), 10)
  wavelength = (3 * pow(10, 8)) / (2.4 * pow(10, 9))
  #print(20 * math.log(((4 * 3.1415 * 30) / wavelength),10))
  #print(wavelength)
  return (d + f + c - 2.85 - 2.85)



def pathLossVanilla(distance, pathLossExponent, transmitterPower):
  """
  distance: the distance between the emitting device and the sensor
  pathLossExponent: the path loss exponent used in calculation. For urban areas, this value is between 2.7 and 3.5
  For rural areas, this value is 2, and for suburban areas it is between 3 and 5
  transmitterPower: this value is in dBm and is the transmitter power of the emitting device, not the sensor.
  Description: In our case, fanchen used an emitter that had a transmission power of 30 dBm
  Using the formula L = 10*n*long_10(d) + C
  """
  idealRssi = transmitterPower + 10 * pathLossExponent * math.log10(distance)
  return idealRssi
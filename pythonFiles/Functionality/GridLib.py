"""
In the GridLib library, we have functions that were used to create, visualize, and analyze 
information that was used in creating the grid that lays over Clematis Street. In here, we
can create any size grid on any location on the earth. 
"""
from geopy import distance
from math import pi, cos
import folium, numpy as np, matplotlib.pyplot as plt, sys, pandas as pd
import webbrowser, random, csv, json, math, random

sys.path.append("pythonFiles")

from Functionality import TrilaterationLib as tl
from Functionality import PathLossLib as pl
from Functionality import DataFiltrationLib as dfl

# -----------------------------------------------------------------------------------------
# FANCHEN FUNCTIONS 
#  
# This is the class for a grid square
class GridSquare:
  """
  location: a coordinate value that represents grid tile location in the grid
  corners: the (lat, long) values for the corder of each grid tile
  center: center latitude and longitude for the grid square
  sensor_distance: distances between the center of the tile and each sensor in the grid
  calculated_RSSI: using a pathloss model, represents "ideal" rssi value
  avg_RSSI: a calculated average value use when we know the location of emitters. Only 
  meaningful when the tile contains the location of a known emitter locations
  mode_RSSI: a calculated mode value use when we know the location of emitters. Only 
  meaningful when the tile contains the location of a known emitter locations
  best_RSSI: a calculated best value use when we know the location of emitters. Only 
  meaningful when the tile contains the location of a known emitter locations
  is_emitter: a boolean value. True if emitter is in this tile, False if not. Only
  meaningful when we know the locations of emitting devices.
  score: mathematical result dealing with the difference between calculated_RSSI and
  actual rssi values. Only meaningful for tiles with is_emitter = True
  hasSensor: True if the tile has a sensor within its boundries, False otherwise
  localizationGuesses: a dictionary that contains localization guesses based on 
  known emitter locations and data from those emitters.
  """
  def __init__(self, location, corners, center, sensor_distances, calculated_RSSI, avg_RSSI,
              is_emitter, score, hasSensor, localizationGuesses): #changed actual_RSSI to avg_RSSI
    # contains all necessary variables for a grid square
    self.location = location
    self.corners = corners
    self.center = center
    self.sensor_distances = sensor_distances
    self.calculated_RSSI = calculated_RSSI
    self.avg_RSSI = avg_RSSI
    self.is_emitter = is_emitter
    self.score = score
    self.hasSensor = hasSensor #KYLE ADDED THIS ATTRIBUTE ON 7/11/23
    self.localizationGuesses = localizationGuesses #Kyle added this attribute on 7/31/23


def adjustedLongitude(t, x):
  """
  t: the tuple of (lat,long) of reference location.
  x: is the distance, in meters, from the reference point.
  Returns: a new (lat,long) that is adjusted by x meters
  Description: If x is positive, this distance is eastward.
  If x is negative, this distance is westward.
  """
  rEarth = 6371000.0
  newLongitude = t[1] + (x / rEarth) * (180/pi) / cos(t[0] * pi/180)
  return (t[0], newLongitude)

def adjustedLatitude(t, y):
  """
  t: the tuple of (lat,long) of reference location.
  y: is the distance, in meters, from the reference point.
  Returns: a new (lat,long) that is adjusted by y meters
  Description: If y is positive, this distance is northward.
  If y is negative, this distance is southward.
  """
  rEarth = 6371000.0
  newLatitude  = t[0]  + (y / rEarth) * (180 / pi)
  return (newLatitude, t[1])


def visualizeGrid(origin, lat_dist, long_dist, meridianDist, parallelDist):
  """
  Origin: southwest point of grid
  lat_dist: how far, in meters, the grid will expand east
  long_dist: how far, in meters, the grid will expand north
  meridianDist: how many steps, in meters, are between captured meridian lines
  parallelDistL how many steps, in meters, are between captured parallel lines
  Returns: a folium map object
  Description: This function will plot the grid onto a folium map and return the
  object. It is up to another function to save the file in html format
  """
  latList, longList = createGrid(origin, lat_dist, long_dist, meridianDist, parallelDist)
  latList = latList[:-1]
  longList = longList[:-1]
  m = folium.Map(location=origin, width=2000, height=900, zoom_start=19, max_zoom=21)
  parimeter = [origin,
               (origin[0], longList[-1]),
               (latList[-1], longList[-1]),
               (latList[-1], origin[1]),
               origin]
  folium.PolyLine(locations=parimeter).add_to(m)
  loc = origin
  for i in range(int(lat_dist/meridianDist)): #how many times I want to create a parallel line
    loc = adjustedLongitude(t=loc, x=meridianDist)
    up = adjustedLatitude(t=loc, y=long_dist)
    locationList=[loc, up]
    folium.PolyLine(locations=locationList).add_to(m) #create the lines along meridian (up and down lines)
  loc = origin
  for i in range(int(long_dist/parallelDist)):
    loc = adjustedLatitude(t=loc, y=parallelDist)
    right = adjustedLongitude(t=loc, x=lat_dist)
    locationList=[loc, right]
    folium.PolyLine(locations=locationList).add_to(m) #create the lines along the parallel (left to right lines)
  return m


def showGrid(m, filePath):
  """
  m: the folium Map object
  filePath: The path to which you want to save your html map
  Returns: a new file with specified filePath. must be an html file.
  Description: This function will create a visual rendering of the given map object
  """
  m.save(filePath)
  webbrowser.open(filePath, new=2)

def multipleGrids(listOfGrids, parentOrigin):
  """
  listOfGrids:  a list of lists where each list contains the raw parameters needed 
  to make a grid. The order is as follows:
                grid[0] = origin
                grid[1] = lat_dist
                grid[2] = long_dist
                grid[3] = meridianDist
                grid[4] = parallelDist
  parentOrigin: The focal point of the overall map
  Returns: a folium.Map object
  Description: Displays multiple grid visuals into one map so we can see how all our grids look
  like in one place
  """
  m = folium.Map(location=parentOrigin, width=2000, height=900, zoom_start=19, max_zoom=21)
  for grid in listOfGrids:
    latList, longList = createGrid(grid[0], grid[1], grid[2], grid[3], grid[4])
    #latList, longList = createGrid(origin, lat_dist, long_dist, meridianDist, parallelDist)
    latList = latList[:-1]
    longList = longList[:-1]
    parimeter = [grid[0],
                (grid[0][0], longList[-1]),
                (latList[-1], longList[-1]),
                (latList[-1], grid[0][1]),
                grid[0]]
    folium.PolyLine(locations=parimeter).add_to(m)
    loc = grid[0]
    for i in range(int(grid[1]/grid[3])): #how many times I want to create a parallel line
      loc = adjustedLongitude(t=loc, x=grid[3])
      up = adjustedLatitude(t=loc, y=grid[2])
      locationList=[loc, up]
      folium.PolyLine(locations=locationList).add_to(m) #create the lines along meridian (up and down lines)
    loc = grid[0]
    for i in range(int(grid[2]/grid[4])):
      loc = adjustedLatitude(t=loc, y=grid[4])
      right = adjustedLongitude(t=loc, x=grid[1])
      locationList=[loc, right]
      folium.PolyLine(locations=locationList).add_to(m) #create the lines along the parallel (left to right lines)
  return m

def createGrid(origin, latDistance, longDistance, adjustedMeridianDistance, adjustedParallelDistance):
  """
  Origin: southwest point of grid as a tuple
  latDistance: how far, in meters, the grid will expand east
  longDistance: how far, in meters, the grid will expand north
  adjustedMeridianDistance: how many steps, in meters, are between captured meridian lines
  adjustedParallelDistance: how many steps, in meters, are between captured parallel lines
  Returns: the latList and longList that define the boundaries and tiles of the grid
  Description:
  This function will return two lists - latList and longList.
  These list will contain the parallels(latitude) and meridians(longitude) that
  are involved in this graph that are separated by the corresponding adjusted distances.
  This function requires an origin point as a tuple,
  the distance(meters) of how far up in longitude from the origin as a positive integer,
  and the distance of how far right in latitude we stray from the origin as a positive integer
  """
  #latDistance = latDistance - 1
  #longDistance = longDistance - 1
  longList = list()
  latList = list()
  longList.append(origin[1])
  latList.append(origin[0])

  #ORIGINAL
  #find the longitude points of separated meridians
  coords = origin
  for i in range(int(latDistance/adjustedMeridianDistance)):
    coords = adjustedLongitude(coords, adjustedMeridianDistance)
    longList.append(coords[1])
    #is the last item in this list 170 m from origin
  if latDistance % adjustedMeridianDistance != 0:
    raise Exception("distance between meridans wasn't evenly split for latDistance = " + str(latDistance) +
                    "\nlatDistance % adjustedMeridianDistance must equal 0")
  print(distance.distance(origin, (origin[0], longList[-1])).meters)

  #ORIGINAL
  coords = origin
  for i in range(int(longDistance/adjustedParallelDistance)): #this is resulting in a decimal sometimes 20/85 when i should be doing 170/85 to count how many parallel lines to add in grid
    coords = adjustedLatitude(coords, adjustedParallelDistance)
    latList.append(coords[0]) #appending the parallels within the grid
  #if the adjustedParallelDistance isnt evenly divisible, we do this
  if longDistance % adjustedParallelDistance != 0:
    raise Exception("distance between parallels wasn't evenly split for longDistance = " + str(longDistance) +
                    "\n longDistance % adjustedParallelDistance must equal 0")
    #latList.append(adjustedLatitude(origin, longDistance)[0]) #why is this here???

  return latList, longList


# This function makes a 2D array of all possible lat/long combinations
def makeCoordsArray(latList, longList):
  """
  latList: latList from createGrid
  longList: longList from createGrid
  Returns: a 2D array of coordinates
  Description: This function makes a 2D array of all possible lat/long combinations
  """
  all_coords = np.zeros((len(latList),len(longList)), dtype=tuple)
  for i in range(len(latList)):
    for j in range(len(longList)):
      all_coords[i][j] = (latList[i], longList[j])
  return all_coords


def getGridCorners(coord_array):
  """
  coord_array: the return value from makeCoordsArray(latList, longList)
  Returns: an array of all grid corners
  Description: This function created the grid. Using the coords 2D array, it goes
  to every index and stores the 4 coords in each grid square. It also can handle
  reaching the end of the grid.
  """
  # makes a new array with the same shape as the coord array
  grid_array = np.zeros(coord_array.shape, dtype=tuple)
  print("What is the shape of grid_array\n", coord_array.shape) #should be 5,25
  itr = np.nditer(grid_array, flags=['multi_index', 'refs_ok'])
  for x in itr:
    # Following code saves coords of the 4 corners of each grid position
    # The corners are always saved in the same order
    # That is, bottom left, bottom right, top left, top right
    # ignores the cells in top row and last column
    if (itr.multi_index[0] != grid_array.shape[0] - 1) & (itr.multi_index[1] != grid_array.shape[1] - 1):
      grid_array[itr.multi_index] = (coord_array[itr.multi_index],
                                  coord_array[itr.multi_index[0], itr.multi_index[1] + 1],
                                  coord_array[itr.multi_index[0] + 1, itr.multi_index[1]],
                                  coord_array[itr.multi_index[0] + 1, itr.multi_index[1] + 1])
      
  # deletes the top row and last column
  # just needed them to get the corners for the edge cells
  grid_array = np.delete(grid_array, grid_array.shape[0] - 1, 0)
  grid_array = np.delete(grid_array, grid_array.shape[1] - 1, 1)

  return grid_array


def getEmitterCoords(df):
  """
  df: a dataframe object that has known emitter locations
  Returns: a dictionary that contains the emitter location and its geographical
  coordinate values
  Description: The function gets the coordinates of all emitter locations in
  the given data frame.
  """
  ref = df['ref_sensor'].unique() # gets array of all ref_sensors
  x = df['x'].unique() # gets 2D array of all X values
  x = x[:5] # gets rid of x = 20, since there are barely any and it only complicates things
  emitter_coords = {}
  for i in ref:
    for j in x:
      emitter_coords.update({f"{i}, {float(j)}": (adjustedLongitude(tl.getCoordinates(str(i)), j))})
      # makes a dict with ref_sensor and x as key, and coordinates of emitter as value
      # ex: {'22, 0.0': (26.713399, -80.056938), '22, 4.0': (26.713399, -80.056897728846), etc}
  return emitter_coords


# This function gets the position of emitters within the grid
def getEmitterPositions(emitter_coords, latList, longList, grid_corners):
  """
  emitter_coords: return value from getEmitterCoords(df)
  latList: return value from createGrid(origin, latDistance, longDistance, adjustedMeridianDistance, adjustedParallelDistance)
  longList: return value from createGrid(origin, latDistance, longDistance, adjustedMeridianDistance, adjustedParallelDistance)
  grid_corners: return value from getGridCorners(coords_array)
  Returns: a dictionary that tells us the tile location of each emitter
  Description: This function gets the positions of emitters within the grid
  """
  emitter_position = {}
  latList = latList[:-1]
  longList = longList[:-1]
  for i, j in emitter_coords.items():
    # calls getDeviceGridSpot to find where the emitter would be in the grid
    # ex: emitter at 22, 4.0 might be at (4, 16) (random spot not accurate)
    loc = getDeviceGridSpot(j, latList, longList, grid_corners)
    # if -1 is returned, then that sensor/x pair is not in the grid
    if loc == -1:
      emitter_position.update({i: -1})
    else:
      emitter_position.update({i: loc})
      # dict has format of sensor, x pair as key and grid position (or -1) as value
      # ex: {'22, 0.0': -1, '22, 4.0': (1, 3), etc}
  return emitter_position

# This function checks if the given device is within the bounds of the grid
# If it is, it compares coordinates with the lat/long lists until the
# lat/long coords are larger
# It returns a tuple of 4 coords representing the 4 corners of the grid square
# the device is in
# If it is not in bounds, it returns -1
def getDeviceGridSpot(device_loc, latList, longList, grid_corners):
  """
  device_loc: return values from getEmitterCoords(df)
  latList: return value from createGrid(origin, latDistance, longDistance, adjustedMeridianDistance, adjustedParallelDistance)
  longList: return value from createGrid(origin, latDistance, longDistance, adjustedMeridianDistance, adjustedParallelDistance)
  grid_corners: return value from getGridCorners(coords_array)
  Returns: a tuple of 4 coords representing the 4 corners of the grid square the
  device is in, -1 if the device is not within the grid.
  Description: This is a helper function for getEmitterPositions(). This function
  checks if the given device is within the bounds of the grid. If it is, it compares
  coordinates with the lat.long lists until the lat/long coords are larger. It
  returns a tuple of 4 coords representing he 4 corners of the grid square the
  device is in. If it is not in bounds, it returns -1
  """
  latList = latList[:-1]
  longList = longList[:-1]
  
  # checks if device_loc latitude is within grid bounds
  lat_index = 0
  if (max(latList) >= device_loc[0]) & (min(latList) <= device_loc[0]):
    for i in range(len(latList)):
      if (device_loc[0] > latList[i]):
        # keeps comparing until it reaches a latitude that is larger
        lat_index = i
  else:
    print("Inputted coordinates are out of range of grid latitude")
    #print("Please set new coordinates")
    return -1

  # checks if device_loc longitude is within grid bounds
  long_index = 0
  if (max(longList) >= device_loc[1]) & (min(longList) <= device_loc[1]):
    for i in range(len(longList)):
      if (device_loc[1] > longList[i]):
        # keeps comparing until it reaches a longitude that is larger
        long_index = i
  else:
    #print("Inputted coordinates are out of range of grid longitude")
    #print("Please set new coordinates")
    return -1

  coord_1 = (latList[lat_index], longList[long_index]) # bottom left corner
  coord_2 = (latList[lat_index], longList[long_index + 1]) # bottom right
  coord_3 = (latList[lat_index + 1], longList[long_index]) # top left
  coord_4 = (latList[lat_index + 1], longList[long_index + 1]) # top right
  device_coords = (coord_1, coord_2, coord_3, coord_4) 

  # this checks if the device coords match with a grid spot
  itr = np.nditer(grid_corners, flags=['multi_index', 'refs_ok'])
  device_loc_index = ()
  for x in itr:
    if grid_corners[itr.multi_index] == device_coords:
      device_loc_index = itr.multi_index

  #print(f'Coord 1: {coord_1}')
  #print(f'Coord 2: {coord_2}')
  #print(f'Coord 3: {coord_3}')
  #print(f'Coord 4: {coord_4}')
  #print("Total Distance from device to coord_1:", distance.distance(device_loc, coord_1).meters)
  #print("Total Distance from device to coord_2:", distance.distance(device_loc, coord_2).meters)
  #print("Total Distance from device to coord_3:", distance.distance(device_loc, coord_3).meters)
  #print("Total Distance from device to coord_4:", distance.distance(device_loc, coord_4).meters)

  # returns tuple containing device's position in the grid (ex. (10, 92))
  return device_loc_index


def makeGridFanchen(grid_corners, latList, longList, emitter_locs, df):
  """
  grid_corners: return value from getGridCorners(coords_array)
  latList: return value from createGrid(origin, latDistance, longDistance, adjustedMeridianDistance, adjustedParallelDistance)
  longList: return value from createGrid(origin, latDistance, longDistance, adjustedMeridianDistance, adjustedParallelDistance)
  emitter_locs: return value from getEmitterPositions(emitter_coords, latList, longList, grid_corners)
  df: a blockData csv file that has known emitter locations
  Returns: a grid object that uses the gridSquare class
  Description: This function uses a bunch of information from different functions to
  create a grid object. This object holds all the gridSquares we made and we can
  call all of them by location, hasSensor, etc. This is basically our core
  value when we try to localize emitter locations because we do so within the boundaires
  of this grid.
  the df should be of blockData right now since that is what we have been working with so far
  when we know the locations of emitting devices, like in Fanchens dataset.
  """

  # --------------------------
  # These sensor lists are SPECIFICALLY for block 500 from Fanchen's data on 2022_11_17
  # Different days might have different sensors used so you NEED to change this if you want to use
  # a different day, and especially if you want to use block 400 instead

  # RSSI sensor list means sensors that received RSSI values, missing sensors had empty columns
  RSSI_sensor_list = ('57', '20', '05', '34', '22', '06', '31', '36', '35') 
  # ref sensor list means sensors that were used as a reference point for determining location,
  # not all sensors were used as a refernece ON THIS DAY
  ref_sensor_list = ('57', '20', '54', '40', '34', '22', '42', '31', '33', '36', '35') 
  # --------------------------

  latList = latList[:-1]
  longList = longList[:-1]

  grid = np.zeros(grid_corners.shape, dtype=GridSquare)
  print("What is the shape of the grid\n", grid_corners.shape) #6,26 when it should be 5,25

  itr = np.nditer(grid, flags=['multi_index', 'refs_ok'])
  for x in itr:
    is_emitter = False
    # just stores the location of the grid square in the grid
    location = itr.multi_index
    # calculates center lat/long by taking average of the lat and long of the corners
    center_lat = (grid_corners[itr.multi_index][0][0] + grid_corners[itr.multi_index][2][0]) / 2
    center_long = (grid_corners[itr.multi_index][0][1] + grid_corners[itr.multi_index][1][1]) / 2

    for i, j in emitter_locs.items():
      if (j == itr.multi_index):
        is_emitter = True
        break

    sensor_distances = {}
    calculated_RSSI = {}
    avg_RSSI = {}
    scores = {}

    # goes through the list of sensors and gets their distances to the grid center
    # and all related RSSI values (when that is implemented)
    for i in RSSI_sensor_list:
      # calculates distances to all sensors
      sensor_distances.update({i: distance.distance(tl.getCoordinates(i), (center_lat, center_long)).meters})
      # gets calculated RSSIs for all sensors from path loss model
      calculated_RSSI.update({i: pl.pathLossExponent(sensor_distances[i])})

      # frankly, avg rssi is not really used for anything, but we're just going to keep it in
      # PHILLIP'S AVG RSSI STUFF ------------------------------------------------------------------------------------------
      # checks if square is an emitter location
      if is_emitter == True:
        avg_Actual_RSSI = averageActualRSSI(emitter_locs, df, ref_sensor_list)
        for key in avg_Actual_RSSI:
          # checks if current grid position matches position of anything in RSSI dict
          if itr.multi_index == key:
            # updates actual_RSSI field for GridSquare class with avg_RSSI for every sensor
            avg_RSSI.update({i: avg_Actual_RSSI[key]['s'+str(i)]})
        # subtracts calculated_RSSI and actual_RSSI to get score for every sensor
        scores.update({i: abs(calculated_RSSI[i] - avg_RSSI[i])})
      else:
        # if square is not an emitter location, then actual_RSSI and score are given placeholder numbers
        avg_RSSI.update({i: -9999})
        scores.update({i: -9999})
      # PHILLIP END------------------------------------------------------------------------------------------

    # creates the grid square object
    grid_square = GridSquare(location, grid_corners[itr.multi_index],
                            (center_lat, center_long), sensor_distances,
                            calculated_RSSI, avg_RSSI, is_emitter, scores , [], {})

    #FOLLOWING BLOCK IS FROM KYLE FOR HASSENSOR ------------------------------------
    #get list of sensors that have true as value
    hasSensorList = list()
    hasSensor = containsSensor(tile=grid_square, sensorList=RSSI_sensor_list, latList=latList, longList=longList)
    for key, val in hasSensor.items():
      if val == True:
        hasSensorList.append(key)
    grid_square.hasSensor = hasSensorList
    # END KYLE BLOCK ----------------------------------------------------------------

    # adds grid square object to grid array
    grid[itr.multi_index] = grid_square

  return grid


def exportGridAsCsv(grid, pathName, withIndex):
  """
  grid: return value from makeGridFanchen()
  pathName: the desired path name to save the returned csv file
  withIndex: set to True if you want the csv file to have an index column. False
  if otherwise.
  Returns: a csv file form of the grid object
  Description: This function flattens a grid into rows and columns so that we 
  can turn it into a csv file and work with the data of the grid
  """
  yea = grid.flatten()
  grid_df = pd.DataFrame.from_records(vars(o) for o in yea)
  grid_df.to_csv(pathName, index=withIndex)


def sensorLocationsDict(sensorList):
  """
  sensorList: string list that indicates sensor numbers
  Returns: a dictionary that contains the sensor number as the key and the (lat, long)
  of the sensor as the value, which is the physical location of a sensor
  Description: This function takes in a list of sensor numbers and returns a dictionary
  that contains the sensor number as the key and the (lat,long) of the sensor as the value
  """
  sensorLocations = {}
  for sensor in sensorList:
    coord = tl.getCoordinates(sensor)
    sensorLocations.update({sensor: coord})

  return sensorLocations


def sensorMaxCoords(sensorList, latList, longList):
  """
  sensorList: string list that indicates sensor numbers
  latList: list of parallels that make up the current grid
  longList: list of meridians that make up the current grid
  Returns: This function will return the maximum latitude and longitude that a sensor is less than, according to grid restrictions.
  Description: when we reach the first latitude that is larger than the latitude of the sensor, we
  collect this latitude and store it as the max latitude. This helps us determine what tile we are in
  within our grid.
  """
  maxCoordsDict = {}
  sensorLocations = sensorLocationsDict(sensorList)

  for sensor, coords in sensorLocations.items():
    for i in range(len(latList)):
      if(latList[i] > coords[0]):
        for j in range(len(longList)):
          if(longList[j] > coords[1]):
            #do out stuff
            maxCoords = (latList[i], longList[j])
            maxCoordsDict.update({sensor: maxCoords})
            break
        break
  return maxCoordsDict


def containsSensor(tile, sensorList, latList, longList):
  """
  tile: an instance of the GridSquare class
  sensorList: list of strings that indicate sensor numbers
  latList: list of parallels that make up the current grid
  longList: list of meridians that make up the current grid
  Returns: a dictionary with key as sensor and value as a boolean that indicates
  if the sensor is within the tiles border
  Description: In this function, we check if any of the sensors in the sensor list are within
  the given tile Cell. 
  """

  tileDict = {}
  maxCoordsDict = sensorMaxCoords(sensorList, latList, longList)
  for sensor, coord in maxCoordsDict.items():
    if coord == tile.corners[3]:
      tileDict.update({sensor: True})
    else:
      tileDict.update({sensor: False})
  return tileDict


def averageActualRSSI(emitter_locs, df, ref_sensor_list):
  """
  emitter_locs: return value from getEmitterPositions(emitter_coords, latList, longList, grid_corners)
  df: a blockData csv file that has known emitter locations
  ref_sensor_list: a list of reference sensors
  Returns: a dictionary of average rssi values for emitters
  Description: finds the average rssi value for each sensor/emitter pair. 
  """
  RSSI = {}
  for i in ref_sensor_list:
    x = 0.0 #Kyle: turned this to int instead of float bc was getting keyError
    # Phillip changed it back because was getting keyError 
    while x <= 16.0:
      mean = df.loc[(df['x'] == x) & (df['ref_sensor'] == int(i))].mean()
      mean = mean.iloc[2:]
      if emitter_locs[f"{i}, {x}"] != -1:
        RSSI.update({emitter_locs[f"{i}, {x}"]: mean})
      x += 4.0
  return RSSI


def completeGridFanchen(origin, latDistance, longDistance, adjustedMeridianDistance, adjustedParallelDistance, df500):
  """
  origin: a tuple of coordinates where the bottom left of the grid will start
  latDistance: how far we want the latitide lines to go (horizontal lines)
  longDistance: how far we want the longitidue lines to go (vertical lines)
  adjustedMeridianDistance: the space between meridian lines
  adjustedParallelDistance: the space between parallel lines
  df500: should be a blockData csv file
  Returns: a grid object
  Description: The result of this function will return all created objects that are constructed while creating a grid.
  This information will be in the form of a tuple as (grid, emitter_locs, emitter_coords, grid_corners, coords_array, latList, longList)
  calling an index from this tuple will give you the information you want went you create a grid.
  There were a lot of functions that go into creating a grid, so it was a lot easier to put them all into one
  function
  """
  latList, longList = createGrid(origin=origin, latDistance=latDistance, longDistance=longDistance,
                                  adjustedMeridianDistance=adjustedMeridianDistance, 
                                  adjustedParallelDistance=adjustedParallelDistance)
  coords_array = makeCoordsArray(latList, longList) # makes 2D array with all lat/long
  grid_corners = getGridCorners(coords_array) # stores the corner coordinates of all grid squares
  emitter_coords = getEmitterCoords(df500) # finds the coordinates of the all emitters 
  emitter_locs = getEmitterPositions(emitter_coords, latList, longList, grid_corners) # gets the location of emitters with in the grid
  grid = makeGridFanchen(grid_corners, latList, longList, emitter_locs, df500) # creates grid composed of GridSquare objects
  return (grid, emitter_locs, emitter_coords, grid_corners, coords_array, latList, longList)

# THIS IS THE FUNCTION USED FOR LOCALIZATION IN MINI-GRID
def localizationTest(grid, df, emitter_locs):
  """
  grid: a grid object made from completeGridFanchen()
  df: a blockData csv file that has known emitter locations
  emitter_locs: a list of the locations of emitters from getEmitterPositions()
  returns: A historgram graph that shows the distance error of localized probe requests
  I will also be returing a dataframe that contains all the rows in the df that were
  considered emitter locations plus their distance error after localization
  """
  data = list() #to hold data for the returned data frame

  iteration_size = 0
  if (df.shape[0] < 100):
    iteration_size = df.shape[0] - 1
  else:
    iteration_size = 100

  random.seed(0) # ensures same numbers are chosen
  count = 0
  results = np.zeros(iteration_size) # creates empty numpy array to hold results
  loc_list = [] # list for storing guessed locations

  # runs localization however many times
  while count < iteration_size:
    rand_row = random.randint(0,df.shape[0] - 1) # picks number from 0 to size of dataframe - 1
    device_row = df.iloc[rand_row] # gets random row 
    position = device_row[0:2] # stores ref_sensor and x
    
    #just focusing in on the emitter locations in this if statement
    if emitter_locs[f'{int(position.iloc[1])}, {position.iloc[0]}'] != -1:
      device_loc, distance_error = gridLocalizationTest(grid, df, emitter_locs, rand_row) # calls localization function
      loc_list.append(device_loc) # stores guessed location results
      results[count] = distance_error # stores distance error results

      #add distance error to device_row series
      ser = pd.Series([distance_error])
      ser.index = ["distance_error"]
      device_row = pd.concat([device_row, ser])
      data.append(device_row)
      count += 1

  print("Mean: ", results.mean())
  print("Median: ", np.median(results))
  fig, ax = plt.subplots(figsize=(15,5))
  plt.hist(results, bins=20, linewidth=0.5, edgecolor="white")
  plt.axvline(x=np.median(results), color='red', linestyle='--') #median line
  ax.set_xlabel('distance error')
  ax.set_ylabel('count')
  ax.set_title(f'log with distance > 10, Grid shape: {grid.shape}, Mean: {round(results.mean(), 2)}, Median: {np.median(results)}')
  plt.show()
  
  result_df = pd.DataFrame(data=data)
  return loc_list, results, result_df

def gridLocalizationTest(grid, df, emitter_locs, rand_row):
  """
  grid: a grid object made from completeGridFanchen()
  df: a blockData csv file that has known emitter locations
  emitter_locs: a list of the locations of emitters from getEmitterPositions()
  rand_row: a randomly chosen number between 0 and the dataframe size
  Returns: The distance between the localization estimate and 
  the actual location is calculated and returned, as well as the guessed location.  
  Description: This is our attempt at trying to localize an emitter location. In
  this case, we have known emitter locations. When we use data to try to find the
  actual location of the emitter, we can find a distance error between the
  localized point and the actual location of the emitter.
  """

  # gets list of sensors in data
  df_columns = df.columns[2:]
  RSSI_sensor_list = []
  for i in df_columns:
    RSSI_sensor_list.append(i[1:])
    # i[1:] to remove the s before the sensorid

  device_row = df.iloc[rand_row] # gets random row
  position = device_row[0:2] # stores ref_sensor and x

  RSSI = device_row[2:].to_dict() # stores RSSIs from row into dict
  emitter_grid_loc = emitter_locs[f'{int(position.iloc[1])}, {position.iloc[0]}']
  print(f'Emitter at: sensor = {int(position.iloc[1])}, x = {position.iloc[0]}')
  # checks if device is in grid
  if emitter_grid_loc != -1:
    print("Actual grid loc:", emitter_grid_loc)
  else:
    print("Not in grid")
    print("Actual coords:", adjustedLongitude(tl.getCoordinates(str(int(position.iloc[1]))), int(position.iloc[0])))

  # iterates through grid
  score_list = [] # list to store score dicts
  itr = np.nditer(grid, flags=['multi_index', 'refs_ok'])
  for x in itr:
    scores = {'Location':itr.multi_index} # stores grid location

    # calculates scores for entire grid
    for i, j in grid[itr.multi_index].calculated_RSSI.items():
      
      # subtract calculated RSSI from device RSSI and multiply by log base 10 of sensor distance
      # no absolute values
      score = (RSSI['s'+i] - j) * math.log(grid[itr.multi_index].sensor_distances[i], 10)

      # if sensor is less than 10 m away from cell, ignore it 
      if grid[itr.multi_index].sensor_distances[i] > 10:
        scores.update({i: score})
      
    # add scores for cell into list 
    score_list.append(scores)

  # create dataframe from list of score dicts
  columns = ["Location"]
  columns.extend(RSSI_sensor_list)
  score_df = pd.DataFrame(score_list, columns=columns)
  score_df = score_df.set_index('Location')
  # take average of every row and sort in ascending order
  score_mean = score_df.mean(axis=1).sort_values(ascending=True)

  print("Actual RSSIs:                 ", RSSI)
  # deals with devices that are not in grid
  if emitter_grid_loc != -1:
    avg_method_error = round((distance.distance(grid[score_mean.index[0]].center,
      grid[emitter_locs[f'{int(position.iloc[1])}, {position.iloc[0]}']].center).meters), 2)
    print("Estimated RSSI for actual loc:", grid[emitter_grid_loc].calculated_RSSI)
  else:
    avg_method_error = round((distance.distance(grid[score_mean.index[0]].center,
      adjustedLongitude(tl.getCoordinates(str(int(position.iloc[1]))), int(position.iloc[0]))).meters), 2)

  print("Estimated RSSI at guess loc:  ", grid[score_mean.index[0]].calculated_RSSI)
  print("Guessed loc from average:", score_mean.index[0])
  print('Estimation error from taking average:', avg_method_error, 'meters') # Pythagorean Theorem to calc distance
  print()

  # returns guessed location and how far off it is
  return score_mean.index[0], avg_method_error

def clusterCheck(loc_list, cluster_list, start_loc, grid):
  """
  loc_list: a list containing all guessed locations obtained from localization 
  cluster_list: a list of all tiles that have been found to belong to the cluster
  start_loc: the tile the recursive check starts from
  grid: the 2D array containing grid_square objects
  Returns: returns updated cluster_list with any new tiles that belong to the cluster 
  Description: This function is a recursive function that is used to search all
  adjacent tiles to the start_loc. If a tile is included in the list of guesses, 
  it is added to the cluster_list. Also, that tile is used as a new start_loc and 
  this function is called again on that location. The idea is to radiate outwards from
  the original start_loc, the tile that was guessed most often, and find all guesses that
  are clustered around that location. 
  """
  new_start_loc = 0
  adjacent_guesses = []
  # deals with tiles directly above and below starting tile
  # if one of the tiles is in loc_list, add it to the adjacent list
  if (grid[start_loc].location[0] + 1, start_loc[1]) in loc_list:
    new_start_loc = grid[start_loc].location[0] + 1, start_loc[1]
    adjacent_guesses.append(new_start_loc)
  if (grid[start_loc].location[0] - 1, start_loc[1]) in loc_list:
    new_start_loc = grid[start_loc].location[0] - 1, start_loc[1]
    adjacent_guesses.append(new_start_loc)

  # deals with tiles directly before and after the starting tile horizontally
  if (start_loc[0], grid[start_loc].location[1] + 1) in loc_list:
    new_start_loc = start_loc[0], grid[start_loc].location[1] + 1
    adjacent_guesses.append(new_start_loc)
  if (start_loc[0], grid[start_loc].location[1] - 1) in loc_list:
    new_start_loc = start_loc[0], grid[start_loc].location[1] - 1
    adjacent_guesses.append(new_start_loc)

  # deals with tiles to the top right and bottom left of starting tile
  if (grid[start_loc].location[0] + 1, start_loc[1] + 1) in loc_list:
    new_start_loc = grid[start_loc].location[0] + 1, start_loc[1] + 1
    adjacent_guesses.append(new_start_loc)
  if (grid[start_loc].location[0] - 1, start_loc[1] - 1) in loc_list:
    new_start_loc = grid[start_loc].location[0] - 1, start_loc[1] - 1
    adjacent_guesses.append(new_start_loc)

  # deals with tiles to the top left and bottom right of starting tile
  if (grid[start_loc].location[0] + 1, start_loc[1] - 1) in loc_list:
    new_start_loc = grid[start_loc].location[0] + 1, start_loc[1] - 1
    adjacent_guesses.append(new_start_loc)
  if (grid[start_loc].location[0] - 1, start_loc[1] + 1) in loc_list:
    new_start_loc = grid[start_loc].location[0] - 1, start_loc[1] + 1
    adjacent_guesses.append(new_start_loc)

  adjacent_guesses = list(set(adjacent_guesses)) # gets rid of duplicates

  # stores any guesses that aren't in the cluster list
  # AKA guesses that have not been found yet
  temp_list = []
  for i in adjacent_guesses:
    if i not in cluster_list:
      temp_list.append(i)

  # adds new guesses to list
  cluster_list.extend(temp_list)
  # calls clusterCheck for every guess contained in temp_list and removes duplicates
  for i in temp_list:
    cluster_list.extend(clusterCheck(loc_list, cluster_list, i, grid))
    cluster_list = list(set(cluster_list))

  return cluster_list

def clusterLocalization(loc_list, grid, mini_grid, actual_loc):
  """
  loc_list: a list containing all guessed locations obtained from localization 
  actual_loc: a tuple of the actual location within the grid of the device being localized
  mini_grid: a grid constructed in the same way as the regular grid, only 
  limited to being 10x10 meters, with 0.5 meter cells. Since this function should be 
  run before the creation of a mini-grid, mini_grid is not necessary to run this function.
  Simply pass in [] instead if no mini-grid has been created yet. 
  grid: the 2D array containing grid_square objects
  Returns: a tuple representing the grid location of the most commonly guessed tile or the "mode"
  Description: This function looks at the list of guessed locations and extracts the 
  most common one, the mode, to use as a starting point. From this location, we radiate 
  outwards to find any guesses that are clustered around the starting point. This is done
  by calling the recursive clusterCheck function, which handles the actual search. The idea
  is to filter out any guesses that are very far removed from the most common guess. 
  It is hoped that this is a valid method of filtering out incorrect guesses, while not
  knowing the device's true location. Obviously, since we are using Fanchen's data in this
  case, we do know the true location, but it is still useful to see how the guesses
  cluster. 
  """

  print("Original list length:", len(loc_list))

  # get starting point by finding most common guess
  start_loc = max(set(loc_list), key=loc_list.count)
  # make list with duplicate guesses removed
  loc_list_set = list(set(loc_list))

  print("List length without duplicates:", len(loc_list_set))

  loc_list_set = sorted(loc_list_set)
  print(loc_list_set)

  # creates a list to store the clustered guesses
  # adds the starting location to begin with
  cluster_list = []
  cluster_list.append(start_loc)

  #print(start_loc)
  print()
  # calls the clusterCheck function
  guess_cluster = clusterCheck(loc_list_set, cluster_list, start_loc, grid)
  print()
  guess_cluster = sorted(guess_cluster)
  print("Cluster:", guess_cluster)

  # counts how many guesses are in the cluster out of the total number of guesses
  count = 0
  for i in guess_cluster:
    count += loc_list.count(i)
  print(f"Count total: {count} out of {len(loc_list)}")
  if len(loc_list) != 0:
    print("Cluster representation of total:", round((count / len(loc_list)) * 100, 2),'%')
  print()

  # make dictionary of guesses with guess as key and number of times guessed as value
  guesses_dict = {}
  for i in guess_cluster:
    guesses_dict.update({i: loc_list.count(i)})

  # sort guesses from most to least number of occurences
  guesses_dict = sorted(guesses_dict.items(), key=lambda x:x[1], reverse = True)
  guesses_dict = dict(guesses_dict)

  results = np.zeros(count)
  itr = 0
  average = 0
  # calculate distance error for every guess
  for loc, amount in guesses_dict.items():
    if len(mini_grid) == 0: # this is for if the grid is a full-size grid
      avg_method_error = round(distance.distance(grid[actual_loc].center, grid[loc].center).meters, 2)
    else: # this is for if the grid is a mini-grid
      avg_method_error = round(distance.distance(grid[actual_loc].center, mini_grid[loc].center).meters, 2)

    print(f"{loc} had {amount} guesses with distance error: {avg_method_error} meters")
    average += avg_method_error

    # adds error results to a list
    for j in range(loc_list.count(loc)):
      results[itr] = avg_method_error
      itr += 1

  print(f"Distance Error average: {round(average / len(guess_cluster), 2)} meters")
  print()

  # deals with guesses NOT in the cluster
  print("Guesses not in cluster: ")
  missing_guesses = {}
  for i in loc_list_set:
    if i not in guess_cluster:
      missing_guesses.update({i: loc_list.count(i)})

  # sort from most to least
  missing_guesses = sorted(missing_guesses.items(), key=lambda x:x[1], reverse = True)
  missing_guesses = dict(missing_guesses)

  # calculating error for every guess in dictionary
  average = 0
  for loc, amount in missing_guesses.items():
    if len(mini_grid) == 0:
      avg_method_error = round(distance.distance(grid[actual_loc].center, grid[loc].center).meters, 2)
    else:
      avg_method_error = round(distance.distance(grid[actual_loc].center, mini_grid[loc].center).meters, 2)

    average += avg_method_error
    print(f"{loc} had {amount} guesses with distance error: {avg_method_error} meters")

  print(f"Distance Error average: {round(average / len(missing_guesses), 2)} meters")
  return start_loc

def mini_grid(grid, start_loc, df):
  """
  grid: the 2D array containing grid_square objects
  start_loc: a tuple representing the grid location of the most commonly guessed tile or the "mode"
  df: a dataframe derived from Fanchen's data that contains known emitter locations
  Returns: mini_grid, mini_loc_list, mini_results_list
  mini_grid: a 2D array made in the same method as the normal grid, only limited to being 
  10x10 meters with 0.5 meter cells
  mini_loc_list: a list containing the guesses obtained from running localization on the mini-grid
  mini_results_list: a list containing the distance errors of the mini_loc_list
  Description: This function's purpose is to "zoom in" on the full-size grid. The hope is that,
  after clustering and finding the most likely device position, running localization again
  on a smaller grid around that position will obtain even more accurate results. The mini-grid works
  by starting from the start_loc, and expanding 5 tiles in every direction. This effectively leaves 
  the start_loc in the center of the mini-grid. A new grid is then created within these boundaries,
  with smaller tile sizes. After the mini-grid is created, localization is run again, but only on 
  the mini-grid. 
  """

  print(grid.shape)
  print("Start_loc: ", start_loc) 

  # creates mini-grid centered around the most guessed location
  # mini grid is 10 m by 10 m, with cells being 0.5 m so grid is actually 20x20

  # gets grid location of bottom left corner for mini grid
  # 5 meters south and 5 meters west of starting location
  # also deals with cases where starting location is close to edge of grid
  lat_bound = start_loc[0] - 5
  long_bound = start_loc[1] - 5
  if lat_bound < 0:
    lat_bound = 0
  if long_bound < 0:
    long_bound = 0
  minigrid_bounds1 = (lat_bound, long_bound)

  # gets grid location of bottom right corner for mini grid
  lat_bound = start_loc[0] - 5
  long_bound = start_loc[1] + 5
  if lat_bound < 0:
    lat_bound = 0
  if long_bound > grid.shape[1] - 1:
    long_bound = grid.shape[1] - 1
  minigrid_bounds2 = (lat_bound, long_bound)

  # gets grid location of top left corner for mini grid
  lat_bound = start_loc[0] + 5
  long_bound = start_loc[1] - 5
  if lat_bound > grid.shape[0] - 1:
    lat_bound = grid.shape[0] - 1
  if long_bound < 0:
    long_bound = 0
  minigrid_bounds3 = (lat_bound, long_bound)

  # gets grid location of top right corner for mini grid
  lat_bound = start_loc[0] + 5
  long_bound = start_loc[1] + 5
  if lat_bound > grid.shape[0] - 1:
    lat_bound = grid.shape[0] - 1
  if long_bound > grid.shape[1] - 1:
    long_bound = grid.shape[1] - 1
  minigrid_bounds4 = (lat_bound, long_bound)

  # creates mini grid of 10 meters by 10 meters with 0.5 meter long cells
  # so grid is 20x20, with origin being the calculated bottom left corner (bound1)
  LAT_DIST = 10
  if abs(minigrid_bounds1[0] - minigrid_bounds3[0]) < 10:
    LAT_DIST = abs(minigrid_bounds1[0] - minigrid_bounds3[0]) + 1
  LONG_DIST = 10
  if abs(minigrid_bounds1[1] - minigrid_bounds2[1]) < 10:
    LONG_DIST = abs(minigrid_bounds1[1] - minigrid_bounds2[1]) + 1

  # bottom left (southwest) corner used for origin 
  origin = (grid[minigrid_bounds1].corners[0])
  print("Origin:", origin)
  print("Bounds: ", minigrid_bounds1, minigrid_bounds2, minigrid_bounds3, minigrid_bounds4)
  mini_latList, mini_longList = createGrid(origin, LAT_DIST, LONG_DIST, .5, .5)

  # calls all the necessary function for grid creation
  mini_coords_array = makeCoordsArray(mini_latList, mini_longList) # makes 2D array with all lat/long
  print("coords:",mini_coords_array.shape)
  mini_grid_corners = getGridCorners(mini_coords_array) # stores the corner coordinates of all grid squares
  print("grid_corners:",mini_grid_corners.shape)
  mini_emitter_coords = getEmitterCoords(df) # finds the coordinates of the all emitters
  mini_emitter_locs = getEmitterPositions(mini_emitter_coords, mini_latList,
                                           mini_longList, mini_grid_corners) # gets the location of emitters with in the grid
  mini_grid = makeGridFanchen(mini_grid_corners, mini_latList, mini_longList, mini_emitter_locs, df)

  print(mini_grid[getDeviceGridSpot(grid[start_loc].center, mini_latList, 
                                    mini_longList, mini_grid_corners)].location)
  print(mini_emitter_locs)

  random.seed(0) # ensures same numbers are chosen
  count = 0
  iteration_size = 0
  if (df.shape[0] < 100):
    iteration_size = df.shape[0] - 1
  else:
    iteration_size = 100
  mini_results_list = np.zeros(iteration_size) # creates empty numpy array to hold results
  # runs localization however many times

  mini_loc_list = []
  while count < iteration_size:

    rand_row = random.randint(0,df.shape[0] - 1) # picks number from 0 to size of dataframe - 1
    loc, error = gridLocalizationTest(mini_grid, df, mini_emitter_locs, rand_row) # calls localization function
    mini_loc_list.append(loc) # stores location guesses
    mini_results_list[count] = error # stores distance error results
    count += 1

  # returns mini-grid, list of guessed locations, and list of errors
  return mini_grid, mini_loc_list, mini_results_list

def gridLocalization(grid, df, emitter_locs):
  """
  grid: a grid object created from makeGridFanchen function in this library
  df: a dataframe that contains x, ref_sensor and some rssi values
  emitter_locs: a dictionary that contains emitter locations within the boundaries
  of the current grid size. A string that represents
  the ref_sensor and x value of an emitter location as the key, and the grid
  coordinates of this position as the value. Can have multiple entries, or just one
  Returns: A list containing tuples of information. These tuples will contain
  two bits of information. tup[0] will contain the emitterLoc. tup[1] will contain
  the dictionary of localization guesses for that emitterLoc.
  Description: This is our attempt at trying to localize an emitter location. In
  this case, we have known emitter locations. When we use data to try to find the
  actual location of the emitter, we can find a distance error between the
  localized point and the actual location of the emitter.
  """
  #Instead of passing just one emitter_loc, I want to pass in 
  #a list of activeEmitters and just go through each of them
  random.seed(0) #ensures same rows are picked
  localizationList = []

  for emitterRef, emitterLoc in emitter_locs.items():
    split = emitterRef.split(",")
    numSplit = [float(i) for i in split]
    numSplit[0] = int(numSplit[0])
    #Here is where I make a subset
    subset = dfl.getSubsetByRefSensorAndX(refSensor=numSplit[0], x=numSplit[1])

    #now pick random row in subset
    rand_row = random.randint(0,subset.shape[0] - 1)
    print("Random Row Index is: ", rand_row)
    device_row = df.iloc[rand_row] #gets random row from subset
    position = device_row[0:2] #stores ref_sensor and x



    RSSI = device_row[2:].to_dict() # stores RSSIs from row into dict
    #emitter_grid_loc = emitter_locs[f'{int(position.iloc[1])}, {position.iloc[0]}']
    #emiter_grid_loc is just the tile location, which in this version is
    #just the emitterLoc value from for loop



    print("AAAAAAAAHHHHHHHHH Actual RSSIs:",RSSI)
    print(f'Emitter at: sensor = {int(position.iloc[1])}, x = {position.iloc[0]}')
    print("Actual grid loc:",emitterLoc)

    # iterates through grid
    score_list = [] # list to store score dicts
    itr = np.nditer(grid, flags=['multi_index', 'refs_ok'])
    for x in itr:
      #iterate through tiles
      scores = {'Location':itr.multi_index} # stores grid location

      # calculates scores for entire grid, this for loop finds the scores for the 9 sensors
      for i, j in grid[itr.multi_index].calculated_RSSI.items():
        
        # subtract calculated RSSI from device RSSI and multiply by log base 10 of sensor distance
        # no absolute values
        score = (RSSI['s'+i] - j) * math.log(grid[itr.multi_index].sensor_distances[i], 10)

        # if sensor is less than 10 m away from cell, ignore it 
        if grid[itr.multi_index].sensor_distances[i] > 10:
          scores.update({i: score})
      #scores has a score for every tile after doing some math with the rssi values from the

      # add scores for cell into list. Score_list has a bunch of dictionaries (scores). entry is a single tile but all tiles are in here
      score_list.append(scores)

    # create dataframe from list of score dicts
    score_df = pd.DataFrame(score_list, columns=['Location','57','20','05','34','22','06','31','36','35'])
    score_df = score_df.set_index('Location')

    # take average of every row and sort in ascending order
    score_mean = score_df.mean(axis=1).sort_values(ascending=True)
    #display(score_mean)

    # gets latitude and longitude distance from actual location
    lat_dist_avg = abs(score_mean.index[0][0] - emitter_locs[f'{int(position.iloc[1])}, {position.iloc[0]}'][0])
    long_dist_avg = abs(score_mean.index[0][1] - emitter_locs[f'{int(position.iloc[1])}, {position.iloc[0]}'][1])

    # takes latitude and longitude distance and uses pythagorean theorem to calculate distance error
    avg_method_error = round(np.sqrt(lat_dist_avg**2 + long_dist_avg**2), 2)

    print("Guessed loc from average:", score_mean.index[0])
    print("Estimated RSSI for this loc:", grid[score_mean.index[0]].calculated_RSSI)
    print('Estimation error from taking average:', avg_method_error, 'meters') # Pythagorean Theorem to calc distance
    print()

    #converting to dict bc this is the standard for this file type
    score_mean = score_mean[:5]
    score_dict = score_mean.to_dict()

    tup = (emitterLoc, score_dict)
    localizationList.append(tup)

  #should return emitterLoc instead of emitter_grid_loc now
  return localizationList


def generateLocalizationGuesses(row, grid, numberOfGuesses, data):
  """
  row: current row in joseData that has real rssi values
  grid. dataframe version of a grid object that the row initally comes from
  numberOfGuesses: the amount of localization guesses we want to return. 1 is the best
  data: a list that will take dictionaries in preparation for a dataframe data.
  Should be empty when first inserting it into this function

  Returns: Does not return anything explicitly, but does add information to data, which
  should be a list variable outside of the function call

  Description: This function is meant to be used in a lambda function for going over rows in the joseData.csv.
  We basically find the best localization guess for each row from the joseData.csv file and appended it to the
  original row. We compile all these updated rows and create data that is prepared for a dataframe (a list with dictionaries)
  """
  #turn row into dict
  rowDict = row.to_dict() #will be appending best localization to this dict
  #gather the rssi values of the current row
  RSSI = row[1:10]
  #begin iteration through the grid
  score_list = []
  itr = np.nditer(grid, flags=['multi_index', 'refs_ok'])
  for x in itr:
    scores = {'Location':itr.multi_index} #contains the current grid location we are gathering scores for

    #calculate scores for the entire grid
    receiverNumber = 0
    for i, j in grid[itr.multi_index].calculated_RSSI.items(): #KeyError???
      #we are using the calculated rssi for the current tile location
      score = (RSSI["receiver_"+str(receiverNumber)] - j) * math.log(grid[itr.multi_index].sensor_distances[i], 10)
      receiverNumber += 1

      # if sensor is less than 10 m away from cell, ignore it 
      if grid[itr.multi_index].sensor_distances[i] > 10:
        scores.update({i: score})

    score_list.append(scores)

  # create dataframe from list of score dicts
  score_df = pd.DataFrame(score_list, columns=['Location','57','20','05','34','22','06','31','36','35'])
  score_df = score_df.set_index('Location')

  # take average of every row and sort in ascending order
  score_mean = score_df.mean(axis=1).sort_values(ascending=True)

  #converting to dict bc this is the standard for this file type
  score_mean = score_mean[:numberOfGuesses]
  score_dict = score_mean.to_dict()

  #store the only key in this dict
  keyName = list(score_dict.keys())[0]

  rowDict.update({"best_tile_localization": keyName })
  rowDict.update({"best_Localization_value": score_dict.get(keyName)})
  data.append(rowDict) #adding to global data so we can turn it into a dataframe


def csvTojson(csvFilePath, jsonPath, removeIndex=False):
  """
  csvFilePath: The path that the current csv file is located
  jsonPath: the path where you want the new json file to be located
  removeIndex: If the csv file has an extra index column, we can remove it by
  setting this parameter to True so our JSON file does not have an index key:value pair
  Returns: a JSON file at the jsonPath location
  Description: Converts a csv file to a json file 
  """
  data = []

  with open(csvFilePath, encoding='utf-8') as csvf:
    csvReader = csv.DictReader(csvf)
    for rows in csvReader:
      if removeIndex == True:
        del rows[""] #getting rid of index row if the df has one
      for key, value in rows.items():
        if key == "mode_RSSI":
          rows[key] = int(value)
        elif key == "best_RSSI":
          rows[key] = int(value)
        elif key == "is_emitter":
          if value == "False":
            rows[key] = False
          elif value == "True":
            rows[key] = True
      data.append(rows)

  with open(jsonPath, 'w', encoding='utf-8') as jsonf:
    jsonf.write(json.dumps(data, indent=4))


def localizecsv(csvFilePath, csvOutputFilePath, localizationData):
  """
  csvFilePath: original csv file we plan to manipulate. Should be the csv file
  for the grid
  csvOutputFilePath: name of new version of csvFilePath
  localizationData: this parameter is a list object. The items in this list are
  lists that contain two types, at [0] a tuple the represents a location on a grid
  and at [1] a dictionary that represents the localization guesses for that grid spot

  Returns: a csv file of a grid object but with data in the localizationGuesses column

  Description: This function will add in data to the localizationGuesses column of each appropriate row.
  We read through a clean csv file, the the rows with the same positions as those in 
  localizationData, and then input the data to the localizationGuesses column of that row.
  A new csv file is generated with this new information so that we preserve the unaltered version
  while also having a new version with this extended data.
  """
  with open(csvFilePath, 'r') as csvInput:
    with open(csvOutputFilePath, 'w') as csvoutput:
      writer = csv.writer(csvoutput)
      reader = csv.reader(csvInput)

      all = []
      row = next(reader) #header row, not needed to read
      all.append(row)

      for row in reader:
        for data in localizationData:
          if str(row[1]) == str(data[0]):
            print("found a match!")
            row[12] = data[1]
            break #stop for loop once we find a match, save some time
        all.append(row)

      writer.writerows(all)

def getActiveEmitterLocs(emitter_locs):
  """
  emitter_locs: a dictionary that contains a bunch of emitter locations that is already
  relevant to a pre-existing grid.
  Returns: a dictionary that contains emitters currently active within a grid
  Description: emitter_locs contains emitters that are not always active in the current grid.
  So this function returns the emitter locations that are currently in the grid.
  This function does not need the grid dimensions, because that is taken care of
  in the getEmitterPositions and getEmitterCoordinates function where we are given all emitter positions
  Within the given dataframe
  """
  activeEmitters = {}
  for key, val in emitter_locs.items():
    if val != -1:
        activeEmitters[key] = val
  return activeEmitters
# FANCHEN END
# -----------------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------------
# MOBINTEL FUNCTIONS 

# For Fanchen's data we typically hard-coded a 25x170 grid for block 500. This function
# is for MobIntel data. It makes customized grid dimensions based on what sensors are 
# in the data given. 
def getGridDimensions(all_data):
  """
  all_data: A dataframe containing RSSI values under columns named 
  after the sensor that received them. 
  Returns: Returns the origin point, length, and width of grid
  Description: 
  This function uses the data contained within the dataframe to determine
  where the origin of the grid should be. It also determines the 
  length and width of the grid by comparing distances between sensors.
  """
  # get placeholder values
  # lowest == smallest lat and long (most southwestern)
  lowest_lat = tl.getCoordinates(all_data.columns[2])[0]
  lowest_long = tl.getCoordinates(all_data.columns[2])[1]

  # furthest = largest lat and long (most northeastern)
  furthest_lat = tl.getCoordinates(all_data.columns[2])[0]
  furthest_long = tl.getCoordinates(all_data.columns[2])[1]

  # go through all included sensors and find which sensor is the most southwestern
  # and which is the most northeastern
  for i in all_data.columns[2:]:
    # gets coords of sensor i as placeholder
    temp_coords = tl.getCoordinates(i)
    # compare with current lowest_lat/long and replace if lower
    if temp_coords[0] < lowest_lat:
      lowest_lat = temp_coords[0]
    if temp_coords[1] < lowest_long:
      lowest_long = temp_coords[1]

    # compare with current furthest_lat/long and replace if higher
    if temp_coords[0] > furthest_lat:
      furthest_lat = temp_coords[0]
    if temp_coords[1] > furthest_long:
      furthest_long = temp_coords[1]

  # use coordinates of most southwestern sensor to get grid origin
  # go a further 8 meters south and west 
  origin = adjustedLongitude((lowest_lat, lowest_long), -8)
  origin = adjustedLatitude(origin, -8)

  furthest_point = (furthest_lat, furthest_long)
  # calculate how far the origin is from the furthest latitude point
  lat_distance = distance.distance(origin, (furthest_lat, origin[1])).meters
  # calculate how far the origin is from the furthest longitude point
  long_distance = distance.distance(origin, (origin[0], furthest_long)).meters

  # makes the grid a little bigger just in case
  LAT_DIST = round((lat_distance * 1.25), 0)
  LONG_DIST = round((long_distance * 1.25), 0)

  # returns origin point of grid, its width, and length 
  return origin, LAT_DIST, LONG_DIST

# This is the class for a grid square
class GridSquareMI:
  def __init__(self, location, corners, center, sensor_distances,
               calculated_RSSI, hasSensor):
    # contains all necessary variables for a grid square
    self.location = location
    self.corners = corners
    self.center = center
    self.sensor_distances = sensor_distances
    self.calculated_RSSI = calculated_RSSI
    self.hasSensor = hasSensor 


# This function creates the final grid
# iterates and creates a GridSquare object before adding it to array
# every GridSquare object has numerous different variables to calculate
def makeGridMI(grid_corners, latList, longList, df):
  """
  grid_corners: return value from getGridCorners(coords_array)
  latList: return value from createGrid(origin, latDistance, longDistance, adjustedMeridianDistance, adjustedParallelDistance)
  longList: return value from createGrid(origin, latDistance, longDistance, adjustedMeridianDistance, adjustedParallelDistance)
  df: a dataframe containing data from MobIntel, compiled by the dataInitialization() function, 
  you probably? could get away with using Fanchen's data here but makeGridFanchen function has support
  for known emitter functions, so use that one
  Returns: a grid object that uses the gridSquareMI class
  Description: This function uses a bunch of information from different functions to
  create a grid object. This object holds all the gridSquares we made and we can
  call all of them by location, hasSensor, etc. This is basically our core
  value when we try to localize device locations because we do so within the boundaries
  of this grid. 
  """
    
  # gets list of sensors used in data
  df_columns = df.columns[2:]
  RSSI_sensor_list = []
  for i in df_columns:
    RSSI_sensor_list.append(i)

  latList = latList[:-1]
  longList = longList[:-1]

  grid = np.zeros(grid_corners.shape, dtype=GridSquare)
  itr = np.nditer(grid, flags=['multi_index', 'refs_ok'])
  for x in itr:
    # just stores the location of the grid square in the grid
    location = itr.multi_index
    # calculates center lat/long by taking average of the lat and long of the corners
    center_lat = round((grid_corners[itr.multi_index][0][0] + grid_corners[itr.multi_index][2][0]) / 2, 7)
    center_long = round((grid_corners[itr.multi_index][0][1] + grid_corners[itr.multi_index][1][1]) / 2, 7)

    sensor_distances = {}
    calculated_RSSI = {}
    # goes through the list of sensors and gets their distances to the grid center
    # and all related RSSI values (when that is implemented)
    for i in RSSI_sensor_list:
      # calculates distances to all sensors
      sensor_distances.update({i: distance.distance(tl.getCoordinates(i),
                                                     (center_lat, center_long)).meters})
      # gets calculated RSSIs for all sensors from path loss model
      calculated_RSSI.update({i: round(pl.pathLossExponent(sensor_distances[i]), 2)})

    # creates the grid square object
    grid_square = GridSquareMI(location, grid_corners[itr.multi_index],
                            (center_lat, center_long), sensor_distances,
                            calculated_RSSI, [])

    # finds out if grid square contains a sensor
    hasSensorList = list()
    hasSensor = containsSensor(tile=grid_square, sensorList=RSSI_sensor_list, 
                               latList=latList, longList=longList)
    for key, val in hasSensor.items():
      if val == True:
        hasSensorList.append(key)
    grid_square.hasSensor = hasSensorList

    # adds grid square object to grid array
    grid[itr.multi_index] = grid_square

  # returns a 2D numpy array representing the grid, with each element being a grid_square object 
  return grid

# This function sets up necessary parameters for gridLocalization function to run. 
# It contains a loop to run localization on multiple random rows, and returns 
# a list of all the locations gridLocalization guessed as having a device. 
def runLocalizationMI(grid, df, grid_corners):
    
  iteration_size = 0
  if (df.shape[0] < 100):
    iteration_size = df.shape[0] - 1
  else:
    iteration_size = 100
  print("Iteraton size:", iteration_size)
  print("Dataframe shape:", df.shape)

  # ----------
  # By default, this code will run localization on 1000 rows (unless the dataframe size is smaller)
  # Uncommenting the rows below will make it so a row is randomly chosen, and the machash in that row
  # is used to get all occurences of that machash in the data
  # This makes it so only a specific machash is being localized, not 1000 random rows 
  #device_row = df.iloc[rand_row]
  #df = df.loc[df['machash'] == device_row['machash']]
  #iteration_size = df.shape[0] - 1
  #display(df)
  # ----------

  random.seed(0) # ensures same numbers are chosen on successive runs
  count = 0
  # runs localization however many times
  loc_list = []
  while count < iteration_size:

    rand_row = random.randint(0,df.shape[0] - 1) # picks number from 0 to size of dataframe - 1
    device_row = df.iloc[rand_row] # gets random row
    print(device_row['machash'])
    estimated_device_loc = gridLocalizationMI(grid, df, rand_row) # calls localization function
    loc_list.append(estimated_device_loc) # stores location guesses
    count += 1

  # return a list of all localized guessesy 
  return loc_list

# This function deals with guessing a device's location in the grid
# Goes through entire grid and compares acutal RSSI to calculated RSSI 
# to obtain a "score". Score is averaged across a row and the row with the 
# lowest score is considered the best guess of a device's location. 
def gridLocalizationMI(grid, df, rand_row):
  """
  grid: a 2D array containing grid_square objects as elements 
  df: a dataframe containing filtered and reorganized MobIntel data
  rand_row: a randomly chosen number between 0 and the dataframe size
  Returns: The guessed location of the device representing the row  
  Description: This is our attempt at trying to localize a device's location. In
  this case, we do not have known emitter locations. As a result, we cannot calculate
  how incorrect the guesses are, so we only return the guessed location. 
  """

  # gets list of sensors in data
  df_columns = df.columns[2:]
  RSSI_sensor_list = [] 
  for i in df_columns:
    RSSI_sensor_list.append(i)

  device_row = df.iloc[rand_row] # gets random row
  RSSI = device_row[2:].to_dict() # stores RSSIs from row into dict

  # iterates through grid
  score_list = [] # list to store score dicts
  itr = np.nditer(grid, flags=['multi_index', 'refs_ok'])
  for x in itr:
    scores = {'Location':itr.multi_index} # stores grid location

    # calculates scores for entire grid
    for i, j in grid[itr.multi_index].calculated_RSSI.items():

      # subtract calculated RSSI from device RSSI and multiply by log base 10 of sensor distance
      score = (RSSI[i] - j) * math.log(grid[itr.multi_index].sensor_distances[i], 10)

      # if sensor is less than 10 m away from cell, ignore it
      if (grid[itr.multi_index].sensor_distances[i] > 10):
        scores.update({i: score})

    # add scores for cell into list
    score_list.append(scores)

  # create dataframe from list of score dicts
  columns = ["Location"]
  columns.extend(RSSI_sensor_list)
  score_df = pd.DataFrame(score_list, columns=columns)
  score_df = score_df.set_index('Location')

  # take average of every row and sort in ascending order
  score_mean = score_df.mean(axis=1).sort_values(ascending=True)

  print("Actual RSSIs:                 ",RSSI)
  print("Estimated RSSI at guess loc:  ", grid[score_mean.index[0]].calculated_RSSI)
  print("Guessed loc from average:", score_mean.index[0])
  print()
  
  # row with lowest score is considered "best" guess and its location is returned
  return score_mean.index[0]

# This function is used to recursively check for guesses that are grouped together.
# The idea is to start with the most guessed location and radiate outwards in all directions.
# If there is a guess adjacent to the start location, we then check all the tiles next 
# to that location, and so on recursively. Hopefully by the end, we have a list of 
# all guesses that are grouped around the most common guess. 
def clusterCheckMI(loc_list, cluster_list, start_loc, grid):
  """
  loc_list: a list containing all guessed locations obtained from localization 
  cluster_list: a list of all tiles that have been found to belong to the cluster
  start_loc: the tile the recursive check starts from
  grid: the 2D array containing grid_square objects as elements
  Returns: returns updated cluster_list with any new tiles that belong to the cluster 
  Description: This function is a recursive function that is used to search all
  adjacent tiles to the start_loc. If a tile is included in the list of guesses, 
  it is added to the cluster_list. Also, that tile is used as a new start_loc and 
  this function is called again on that location. The idea is to radiate outwards from
  the original start_loc, the tile that was guessed most often, and find all guesses that
  are clustered around that location. 
  """

  new_start_loc = 0
  adjacent_guesses = []

  # deals with tiles directly above and below starting tile
  # if one of the tiles is in loc_list, add it to the adjacent list
  if (grid[start_loc].location[0] + 1, start_loc[1]) in loc_list:
    new_start_loc = grid[start_loc].location[0] + 1, start_loc[1]
    adjacent_guesses.append(new_start_loc)
  if (grid[start_loc].location[0] - 1, start_loc[1]) in loc_list:
    new_start_loc = grid[start_loc].location[0] - 1, start_loc[1]
    adjacent_guesses.append(new_start_loc)

  # deals with tiles directly before and after the starting tile horizontally
  if (start_loc[0], grid[start_loc].location[1] + 1) in loc_list:
    new_start_loc = start_loc[0], grid[start_loc].location[1] + 1
    adjacent_guesses.append(new_start_loc)
  if (start_loc[0], grid[start_loc].location[1] - 1) in loc_list:
    new_start_loc = start_loc[0], grid[start_loc].location[1] - 1
    adjacent_guesses.append(new_start_loc)

  # deals with tiles to the top right and bottom left of starting tile
  if (grid[start_loc].location[0] + 1, start_loc[1] + 1) in loc_list:
    new_start_loc = grid[start_loc].location[0] + 1, start_loc[1] + 1
    adjacent_guesses.append(new_start_loc)
  if (grid[start_loc].location[0] - 1, start_loc[1] - 1) in loc_list:
    new_start_loc = grid[start_loc].location[0] - 1, start_loc[1] - 1
    adjacent_guesses.append(new_start_loc)

  # deals with tiles to the top left and bottom right of starting tile
  if (grid[start_loc].location[0] + 1, start_loc[1] - 1) in loc_list:
    new_start_loc = grid[start_loc].location[0] + 1, start_loc[1] - 1
    adjacent_guesses.append(new_start_loc)
  if (grid[start_loc].location[0] - 1, start_loc[1] + 1) in loc_list:
    new_start_loc = grid[start_loc].location[0] - 1, start_loc[1] + 1
    adjacent_guesses.append(new_start_loc)

  adjacent_guesses = list(set(adjacent_guesses)) # gets rid of duplicates

  # stores any guesses that aren't in the cluster list
  # AKA guesses that have not been found yet
  temp_list = []
  for i in adjacent_guesses:
    if i not in cluster_list:
      temp_list.append(i)

  # adds new guesses to list
  cluster_list.extend(temp_list)
  # calls clusterCheck for every guess contained in temp_list and removes duplicates
  for i in temp_list:
    cluster_list.extend(clusterCheckMI(loc_list, cluster_list, i, grid))
    cluster_list = list(set(cluster_list))

  return cluster_list

# This function prepares localization results for clusterCheck. To get the 
# starting location, we find the max in loc_list. It also removes duplicate guesses.
# Afterwards, clusterCheck is called to do the actual clustering. Using the list returned,
# it counts up how many times different locations were guessed, both in cluster and out. 
def clusterLocalizationMI(loc_list, grid):
  """
  loc_list: a list containing all guessed locations obtained from localization 
  actual_loc: a tuple of the actual location within the grid of the device being localized
  grid: the 2D array containing grid_square objects
  Returns: a tuple representing the grid location of the most commonly guessed tile or the "mode"
  Description: This function looks at the list of guessed locations and extracts the 
  most common one, the mode, to use as a starting point. From this location, we radiate 
  outwards to find any guesses that are clustered around the starting point. This is done
  by calling the recursive clusterCheck function, which handles the actual search. The idea
  is to filter out any guesses that are very far removed from the most common guess. 
  It is hoped that this is a valid method of filtering out incorrect guesses, while not
  knowing the device's true location. Since we do not have true device locations with MobIntel 
  data, this is the closest we can get to knowing where the device is, as well as knowing which 
  guesses are very incorrect.
  """

  print("Original list length:", len(loc_list))

  # get starting point by finding most common guess
  start_loc = max(set(loc_list), key=loc_list.count)

  # make list with duplicate guesses removed
  loc_list_set = list(set(loc_list))

  print("List length without duplicates:", len(loc_list_set))

  loc_list_set = sorted(loc_list_set)
  print(loc_list_set)

  # creates a list to store the clustered guesses
  # adds the starting location to begin with
  cluster_list = []
  cluster_list.append(start_loc)

  # calls the clusterCheck function
  guess_cluster = clusterCheckMI(loc_list_set, cluster_list, start_loc, grid)
  print()
  guess_cluster = sorted(guess_cluster)
  print("Cluster:", guess_cluster)

  # counts how many guesses are in the cluster out of the total number of guesses
  count = 0
  for i in guess_cluster:
    count += loc_list.count(i)
  print(f"Count total: {count} out of {len(loc_list)}")
  print("Cluster representation of total:", round((count / len(loc_list)) * 100, 2),'%')
  print()

  # make dictionary of guesses with guess as key and number of times guessed as value
  guesses_dict = {}
  for i in guess_cluster:
    guesses_dict.update({i: loc_list.count(i)})

  # sort guesses from most to least number of occurences
  guesses_dict = sorted(guesses_dict.items(), key=lambda x:x[1], reverse = True)
  guesses_dict = dict(guesses_dict)

  print("Cluster: ")
  for loc, amount in guesses_dict.items():
    print(f"{loc} had {amount} guesses")
  print()

  # deals with guesses NOT in the cluster
  print("Guesses not in cluster: ")
  missing_guesses = {}
  for i in loc_list_set:
    if i not in guess_cluster:
      missing_guesses.update({i: loc_list.count(i)})

  # sort from most to least
  missing_guesses = sorted(missing_guesses.items(), key=lambda x:x[1], reverse = True)
  missing_guesses = dict(missing_guesses)

  for loc, amount in missing_guesses.items():
    print(f"{loc} had {amount} guesses")

  # returns the grid square that was guessed the most 
  return start_loc

# This function creates a mini-grid centered around the most guessed location 
# found in clusterLocalization. The hope is that this 10 x 10 meter mini-grid, 
# which is also using 0.5 x 0.5 meter cells rather than the normal 1 x 1 meter 
# cells, would allow us to "zoom in" and get more accurate results. Also, since
# the cells are 0.5 meters, the mini-grid is actually 20 x 20 cells in size. 
def mini_gridMI(grid, start_loc, df):
  """
  grid: the 2D array containing grid_square objects
  start_loc: a tuple representing the grid location of the most commonly guessed tile or the "mode"
  df: a dataframe derived from Fanchen's data that contains known emitter locations
  Returns: mini_grid, mini_loc_list, mini_results_list
  mini_grid: a 2D array made in the same method as the normal grid, only limited to being 
  10x10 meters with 0.5 meter cells
  mini_loc_list: a list containing the guesses obtained from running localization on the mini-grid
  Description: This function's purpose is to "zoom in" on the full-size grid. The hope is that,
  after clustering and finding the most likely device position, running localization again
  on a smaller grid around that position will obtain even more accurate results. The mini-grid works
  by starting from the start_loc, and expanding 5 tiles in every direction. This effectively leaves 
  the start_loc in the center of the mini-grid. A new grid is then created within these boundaries,
  with smaller tile sizes. After the mini-grid is created, localization is run again, but only on 
  the mini-grid. 
  """

  print(grid.shape)
  print("Start_loc: ", start_loc) 

  # gets grid location of bottom left corner for mini grid
  # 5 meters south and 5 meters west of starting location
  # also deals with cases where starting location is close to edge of grid
  lat_bound = start_loc[0] - 5
  long_bound = start_loc[1] - 5
  if lat_bound < 0:
    lat_bound = 0
  if long_bound < 0:
    long_bound = 0
  minigrid_bounds1 = (lat_bound, long_bound)

  # gets grid location of bottom right corner for mini grid
  lat_bound = start_loc[0] - 5
  long_bound = start_loc[1] + 5
  if lat_bound < 0:
    lat_bound = 0
  if long_bound > grid.shape[1] - 1:
    long_bound = grid.shape[1] - 1
  minigrid_bounds2 = (lat_bound, long_bound)

  # gets grid location of top left corner for mini grid
  lat_bound = start_loc[0] + 5
  long_bound = start_loc[1] - 5
  if lat_bound > grid.shape[0] - 1:
    lat_bound = grid.shape[0] - 1
  if long_bound < 0:
    long_bound = 0
  minigrid_bounds3 = (lat_bound, long_bound)

  # gets grid location of top right corner for mini grid
  lat_bound = start_loc[0] + 5
  long_bound = start_loc[1] + 5
  if lat_bound > grid.shape[0] - 1:
    lat_bound = grid.shape[0] - 1
  if long_bound > grid.shape[1] - 1:
    long_bound = grid.shape[1] - 1
  minigrid_bounds4 = (lat_bound, long_bound)

  # creates mini grid of 10 meters by 10 meters with 0.5 meter long cells
  # so grid is 20x20, with origin being the calculated bottom left corner (bound1)
  LAT_DIST = 10
  if abs(minigrid_bounds1[0] - minigrid_bounds3[0]) < 10:
    LAT_DIST = abs(minigrid_bounds1[0] - minigrid_bounds3[0]) + 1
  LONG_DIST = 10
  if abs(minigrid_bounds1[1] - minigrid_bounds2[1]) < 10:
    LONG_DIST = abs(minigrid_bounds1[1] - minigrid_bounds2[1]) + 1

  # bottom left (southwest) corner used for origin 
  origin = (grid[minigrid_bounds1].corners[0])
  print("Origin:", origin)
  print("Bounds: ", minigrid_bounds1, minigrid_bounds2, minigrid_bounds3, minigrid_bounds4)
  # creates mini_grid
  mini_latList, mini_longList = createGrid(origin, LAT_DIST, LONG_DIST, .5, .5)

  # calls all the necessary function for grid creation
  mini_coords_array = makeCoordsArray(mini_latList, mini_longList) # makes 2D array with all lat/long
  print("coords:", mini_coords_array.shape)
  mini_grid_corners = getGridCorners(mini_coords_array) # stores the corner coordinates of all grid squares
  print("grid_corners:",mini_grid_corners.shape)
  mini_grid = makeGridMI(mini_grid_corners, mini_latList, mini_longList, df)

  random.seed(0) # ensures same numbers are chosen
  count = 0
  iteration_size = 0
  # if the dataframe size is less than 1000, use that as iteration size
  if (df.shape[0] < 1000):
    iteration_size = df.shape[0] - 1
  else:
    iteration_size = 1000
  
  # runs localization iteration_size many times
  mini_loc_list = []
  while count < iteration_size:

    rand_row = random.randint(0,df.shape[0] - 1) # picks number from 0 to size of dataframe - 1
    locs = gridLocalizationMI(mini_grid, df, rand_row) # calls localization function
    mini_loc_list.append(locs) # stores location guesses
    count += 1

  # returns the mini-grid and the list of guessed locations
  return mini_grid, mini_loc_list


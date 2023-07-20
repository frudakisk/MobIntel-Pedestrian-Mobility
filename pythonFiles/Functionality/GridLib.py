from math import pi, cos
from geopy import distance
import folium, numpy as np, sys, pandas as pd, webbrowser, random

sys.path.append("pythonFiles")

from Functionality import TrilaterationLib as tl
from Functionality import PathLossLib as pl



# This is the class for a grid square
class GridSquare:
  def __init__(self, location, corners, center, sensor_distances, calculated_RSSI, avg_RSSI,
               mode_RSSI, best_RSSI, is_emitter, score, hasSensor): #changed actual_RSSI to avg_RSSI
    # contains all necessary variables for a grid square
    self.location = location
    self.corners = corners
    self.center = center
    self.sensor_distances = sensor_distances
    self.calculated_RSSI = calculated_RSSI
    self.avg_RSSI = avg_RSSI
    self.mode_RSSI = mode_RSSI
    self.best_RSSI = best_RSSI
    self.is_emitter = is_emitter
    self.score = score
    self.hasSensor = hasSensor #KYLE ADDED THIS ATTRIBUTE ON 7/11/23


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


def visualizeGrid(origin, lat_dist, long_dist, meridianDist, parallelDist):
  """This function will plot the grid onto a folium map
  Origin: southwest point of grid
  lat_dist: how far, in meters, the grid will expand north
  long_dist: how far, in meters, the grid will expand east
  meridianDist: how many steps, in meters, are between captured meridian lines
  parallelDistL how many steps, in meters, are between captured parallel lines
  Returns: a folium map onject
  """
  latList, longList = createGrid(origin, lat_dist, long_dist, meridianDist, parallelDist)
  m = folium.Map(location=origin, width=2000, height=900, zoom_start=19, max_zoom=21)
  # parimeter = [origin,
  #              (latList[-1],origin[1]),
  #              (latList[-1], longList[-1]),
  #              (origin[0], longList[-1]),
  #              origin]
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
  This function will create a visual rendering of the given map object
  """
  m.save(filePath)
  webbrowser.open(filePath, new=2)


def createGrid(origin, latDistance, longDistance, adjustedMeridianDistance, adjustedParallelDistance):
  """This function will return two lists - latList and longList.
  These list will contain the parallels(latitude) and meridians(longitude) that
  are involved in this graph that are separated by the corresponding adjusted distances.
  origin: a tuple of (latitude, longtitude) coordinates
  latDistance: How long the latitudinal lines of the grid should stretch
  longDistance: How long the longitudinal liens of the grid should stretch
  adjustedMeridianDistance: How many meters should be between each selected meridian line
  adjustedParallelDistance: How many meters should be between each selected parallel line
  This function requires an origin point as a tuple,
  the distance(meters) of how far up in longitude from the origin as a positive integer,
  and the distance of how far right in latitude we stray from the origin as a positive integer"""
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
def makeCoordsArray(lats, longs):
  all_coords = np.zeros((len(lats)-1,len(longs)-1), dtype=tuple)
  for i in range(len(lats)-1):
    for j in range(len(longs)-1):
      all_coords[i][j] = (lats[i], longs[j])
  return all_coords


# This function creates the grid
# Using the coords 2D array, it goes to every index and stores the 4 coords in
# each grid square
# It also can handle reaching the end of the grid
def getGridCorners(coord_array):
  # makes a new array with the same shape as the coord array
  grid_array = np.zeros(coord_array.shape, dtype=tuple)
  itr = np.nditer(grid_array, flags=['multi_index', 'refs_ok'])
  for x in itr:
    # Following code saves coords of the 4 corners of each grid position
    # The corners are always saved in the same order
    # That is, bottom left, bottom right, top left, top right

    # This statement deals with the very last grid spot i.e. (19, 169)
    if (itr.multi_index[0] == grid_array.shape[0] - 1) & (itr.multi_index[1] == grid_array.shape[1] - 1):
      grid_array[itr.multi_index] = (coord_array[itr.multi_index[0] - 1, itr.multi_index[1] - 1],
                            coord_array[itr.multi_index[0] - 1, itr.multi_index[1]],
                            coord_array[itr.multi_index[0], itr.multi_index[1] - 1],
                            coord_array[itr.multi_index[0], itr.multi_index[1]])
    # This statement deals with the last grid row
    elif itr.multi_index[0] == grid_array.shape[0] - 1:
      grid_array[itr.multi_index] = (coord_array[itr.multi_index],
                                coord_array[itr.multi_index[0], itr.multi_index[1] + 1],
                                coord_array[itr.multi_index[0] - 1, itr.multi_index[1]],
                                coord_array[itr.multi_index[0] - 1, itr.multi_index[1] + 1])
    # This statement deals with the last grid column
    elif itr.multi_index[1] == grid_array.shape[1] - 1:
      grid_array[itr.multi_index] = (coord_array[itr.multi_index[0], itr.multi_index[1] - 1],
                            coord_array[itr.multi_index[0], itr.multi_index[1]],
                            coord_array[itr.multi_index[0] + 1, itr.multi_index[1] - 1],
                            coord_array[itr.multi_index[0] + 1, itr.multi_index[1]])
    # This statement deals with the rest
    else:
      grid_array[itr.multi_index] = (coord_array[itr.multi_index],
                                    coord_array[itr.multi_index[0], itr.multi_index[1] + 1],
                                    coord_array[itr.multi_index[0] + 1, itr.multi_index[1]],
                                    coord_array[itr.multi_index[0] + 1, itr.multi_index[1] + 1])

  return grid_array


# This function gets the coordinates of all emitter locations in given dataframe
def getEmitterCoords(df):
  ref = df['ref_sensor'].unique() # gets array of all ref_sensors
  x = df['x'].unique() # gets 2D array of all X values
  x = x[:5] # gets rid of x = 20, since there are barely any and it only complicates things
  emitter_coords = {}
  for i in ref:
    for j in x:
      emitter_coords.update({f"{i}, {j}": (adjustedLongitude(tl.getCoordinates(str(i)), j))})
      # makes a dict with ref_sensor and x as key, and coordinates of emitter as value
      # ex: {'22, 0.0': (26.713399, -80.056938), '22, 4.0': (26.713399, -80.056897728846), etc}
  return emitter_coords


# This function gets the position of emitters within the grid
def getEmitterPositions(emitter_coords, latList, longList, grid_corners):
  emitter_position = {}
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
def getDeviceGridSpot(device_loc, lats, longs, grid_corners):
  lat_index = 0
  if (max(lats) >= device_loc[0]) & (min(lats) <= device_loc[0]):
    for i in range(len(lats)):
      if (device_loc[0] > lats[i]):
        lat_index = i
  else:
    #print("Inputted coordinates are out of range of grid latitude")
    #print("Please set new coordinates")
    return -1

  long_index = 0
  if (max(longs) >= device_loc[1]) & (min(longs) <= device_loc[1]):
    for i in range(len(longs)):
      if (device_loc[1] > longs[i]):
        long_index = i
  else:
    #print("Inputted coordinates are out of range of grid longitude")
    #print("Please set new coordinates")
    return -1

  coord_1 = (lats[lat_index], longs[long_index])
  coord_2 = (lats[lat_index], longs[long_index + 1])
  coord_3 = (lats[lat_index + 1], longs[long_index])
  coord_4 = (lats[lat_index + 1], longs[long_index + 1])
  device_coords = (coord_1, coord_2, coord_3, coord_4)

  # this checks if the device coords match with a grid spot
  itr = np.nditer(grid_corners, flags=['multi_index', 'refs_ok'])
  device_loc_index = ()
  for x in itr:
    if grid_corners[itr.multi_index] == device_coords:
      device_loc_index = itr.multi_index


  return device_loc_index


def makeGrid(grid_corners, latList, longList, emitter_locs, df):
  """
  the df should be df500 right now since that is what we have been working with so far
  """
  RSSI_sensor_list = ('57', '20', '05', '34', '22', '06', '31', '36', '35') #no RSSI values, excluded 04, 54, 40, 42, 33 from original list
  ref_sensor_list = ('57', '20', '54', '40', '34', '22', '42', '31', '33', '36', '35') #missing ref sensors

  grid = np.zeros(grid_corners.shape, dtype=GridSquare)
  df_mean = df.mean(axis=0)
  df_mode = df.mode(axis=0)
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
    mode_RSSI = {}
    best_RSSI = {}
    avg_Score = {}
    mode_Score = {}
    best_Score = {}
    scores = {}

    # goes through the list of sensors and gets their distances to the grid center
    # and all related RSSI values (when that is implemented)
    for i in RSSI_sensor_list:
      # calculates distances to all sensors
      sensor_distances.update({i: distance.distance(tl.getCoordinates(i), (center_lat, center_long)).meters})
      # gets calculated RSSIs for all sensors from path loss model
      calculated_RSSI.update({i: pl.pathLossExponent(sensor_distances[i])})

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
      mode_RSSI.update({i: df_mode.at[0, 's'+i]})
      df_unique = df.drop_duplicates(subset=['s'+i])
      df_unique = df_unique.reset_index()
      #display(df_unique)
      best_RSSI.update({i: -9999})
      for row, index in df_unique.iterrows():
        if abs(calculated_RSSI[i] - df_unique.at[row, 's'+i]) < abs(calculated_RSSI[i] - best_RSSI[i]):
          best_RSSI.update({i:df_unique.at[row, 's'+i]})

    # creates the grid square object
    grid_square = GridSquare(location, grid_corners[itr.multi_index],
                            (center_lat, center_long), sensor_distances,
                            calculated_RSSI, avg_RSSI, -99, -99, is_emitter, scores , [])

    #FOLLOWING BLOCK IS FROM KYLE FOR HASSENSOR ------------------------------------
    #get list of sensors that have true as value function won't run, currently commenting out - Conor
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


def exportGridAsCsv(grid, pathName):
  yea = grid.flatten()
  grid_df = pd.DataFrame.from_records(vars(o) for o in yea)
  grid_df.to_csv(pathName)


def sensorLocationsDict(sensorList):
  """
  sensorList: string list that indicates sensor numbers
  This function takes in a list of sensor numbers and returns a dictionary
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
  This function will return the maximum latitude and longitude that a sensor is less than, according to grid restrictions.
  This means, when we reach the first latitude that is larger than the latitude of the sensor, we
  collect this latitude and store it as the max latitude. This helps us determine what tile we are in
  within our grid."""
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
  In this function, we check if any of the sensors in the sensor list are within
  the given tile Cell. Will return a dictionary with key as sensor and value
  as a boolean that indicates if the sensor is within the tiles border
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
  RSSI = {}
  for i in ref_sensor_list:
    x = 0.0
    while x <= 16.0:
      mean = df.loc[(df['x'] == x) & (df['ref_sensor'] == int(i))].mean()
      mean = mean.iloc[2:]
      if emitter_locs[f"{i}, {x}"] != -1:
        RSSI.update({emitter_locs[f"{i}, {x}"]: mean})
      x += 4
  return RSSI


def completeGrid(latList, longList, df500):
  """
  latList: list of latitude lines
  longList: list of longitude lines
  df500: should be the df500 file
  """
  coords_array = makeCoordsArray(latList, longList) # makes 2D array with all lat/long
  grid_corners = getGridCorners(coords_array) # stores the corner coordinates of all grid squares
  emitter_coords = getEmitterCoords(df500) # finds the coordinates of the all emitters
  emitter_locs = getEmitterPositions(emitter_coords, latList, longList, grid_corners) # gets the location of emitters with in the grid
  grid = makeGrid(grid_corners, latList, longList, emitter_locs, df500) # creates grid composed of GridSquare objects
  return grid

# This block of code deals with guessing a device's location in the grid


def gridLocalization(grid, df500, emitter_locs):
  RSSI_sensor_list = ('57', '20', '05', '34', '22', '06', '31', '36', '35') #no RSSI values, excluded 04, 54, 40, 42, 33 from original list

  # AVG BEGIN ----------------------------------------------------------------------------------
  # This section deals with localization via averaging scores

  df = df500.dropna() # for now I drop all rows that have empty cells
  if grid.shape[0] == 5: # this is a check for if sample grid is being used
    df = df.loc[df['ref_sensor'] == 22]

  # This loop picks random numbers until it one that doesnt return -1
  # not sure why some emitter_locs return -1, have to look into it
  rand_row = 0
  while True:
    rand_row = random.randint(0,df.shape[0])
    device_row = df.iloc[rand_row] # gets random row
    position = device_row[0:2] # stores ref_sensor and x
    if emitter_locs[f'{int(position.iloc[1])}, {position.iloc[0]}'] != -1:
      break
  print(rand_row)

  RSSI = device_row[2:].to_dict() # stores RSSIs from row into dict
  print("Actual RSSIs:",RSSI)
  print(f'Emitter at: sensor = {int(position.iloc[1])}, x = {position.iloc[0]}')
  emitter_grid_loc = emitter_locs[f'{int(position.iloc[1])}, {position.iloc[0]}']
  print("Actual grid loc:",emitter_grid_loc)


  score_df = pd.DataFrame(columns=['Location','57','20','05','34','22','06','31','36','35'])

  # iterates through grid
  itr = np.nditer(grid, flags=['multi_index', 'refs_ok'])
  for x in itr:
    scores = {'Location':itr.multi_index} # stores grid location 

    # calculates scores for entire grid
    for i, j in grid[itr.multi_index].calculated_RSSI.items():
        scores.update({i: abs(j - RSSI['s'+i])})
    # stores as dataframe
    score_df = pd.concat([score_df, (pd.DataFrame.from_dict([scores]))])

  score_df = score_df.set_index('Location')
  # take average of every row and sort in ascending order
  score_mean = score_df.mean(axis=1).sort_values(ascending=True)

  # this is just for distance calc
  lat_dist_avg = abs(score_mean.index[0][0] - emitter_locs[f'{int(position.iloc[1])}, {position.iloc[0]}'][0])
  long_dist_avg = abs(score_mean.index[0][1] - emitter_locs[f'{int(position.iloc[1])}, {position.iloc[0]}'][1])
  # AVG END ----------------------------------------------------------------------------------

  # COMPARISON BEGIN----------------------------------------------------------------------------------
  # This section deals with localization via comparing scores

  # row at 0 used as baseline 
  best_score = score_df.iloc[0] 
  best_score_index = score_df.index[0]

  # iterate through whole score dataframe 
  for index, row in score_df.iterrows():
    count = 0
    for sensor in score_df.columns:
      if row[sensor] < best_score[sensor]:
        # if sensor on current row has a lower score than the sensor in best_score row
        # +1 to count
        count += 1

      # since you aren't going to get a row with all values lower, arbitrarily
      # pick 5 lower values as goal
      # if count gets to 5, then make current row the new best
      if count >= 5:
        best_score = row
        best_score_index = index
        break

  # used for distance calc
  lat_dist = abs(best_score_index[0] - emitter_locs[f'{int(position.iloc[1])}, {position.iloc[0]}'][0])
  long_dist = abs(best_score_index[1] - emitter_locs[f'{int(position.iloc[1])}, {position.iloc[0]}'][1])
  # COMPARISON END ----------------------------------------------------------------------------------

  print("Guessed loc from average:", score_mean.index[0])
  print("Estimated RSSI for this loc:", grid[score_mean.index[0]].calculated_RSSI)
  print('Estimation error from taking average:', round(np.sqrt(lat_dist_avg**2 + long_dist_avg**2), 2), 'meters') # Pythagorean Theorem to calc distance
  print()
  print("Guessed loc from comparing:", best_score_index)
  print("Estimated RSSI for this loc:", grid[best_score_index].calculated_RSSI)
  print('Estimation error from comparing:', round(np.sqrt(lat_dist**2 + long_dist**2), 2), 'meters')

  return score_mean.index[0]

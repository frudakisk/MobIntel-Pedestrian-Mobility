import sys
import pandas as pd
from geopy import distance
import random

sys.path.append("pythonFiles")

from Functionality import GridLib as gl, Constants as c
from Functionality import DataFiltrationLib as dfl, TrilaterationLib as tl

"""
This driver (as well as the GridLib.py file) has two parts: 
One contains the drivers for running our code built for Fanchen Bao's data. This is data that 
Fanchen collected in West Palm Beach on Clematis Street. It is extremely important, as it
contains the true locations of emitters. Using this data, we could try all kinds of methods to
see what would work best for localizing devices on the actual MobIntel data. The vast majority 
of our work was made specifically for this data. It is also important to note that we used
his data from 2022_11_17 and block_500 almost exclusively. If you were to run the code on
a different day, and especially on block_400, you may get errors or things just might not work correctly. 
This is because different days had different sensors actually receive data or get used as a reference sensor. 
Block_400 is also a different area with completely different sensors. 

The MobIntel block is the second part of the driver. The difference between Fanchen's data 
and MobIntel's raw data necessitated rewriting some functions, which will be marked with 
"MI" at the end of the function name if they have a Fanchen equivalent. Most functions are
 fairly similar to their Fanchen counterpart, but make sure you are using the correct one. 
"""

# ----------------------------------------------------
# FANCHEN VERSION OF GRID STUFF

df500 = pd.read_csv("datasets/block_500_only.csv", engine='python')
df500 = df500.drop(columns=("Unnamed: 0"))
origin = (26.713378, -80.05693981171936)
latDistance=170
longDistance=25

#adjusted latitude
newLoc = gl.adjustedLatitude(origin, 20)
#print(newLoc)
#print(distance.distance(newLoc, origin).meters)

#adjusted longitude
newLoc = gl.adjustedLongitude(origin, 20)
#print(newLoc)
#print(distance.distance(newLoc, origin).meters)

#visualize grid
m = gl.visualizeGrid(origin=origin, lat_dist=25, long_dist=5, 
                     meridianDist=1, parallelDist=1)
#gl.showGrid(m, "media/maps/driverGrid.html")

#create grid
latList, longList = gl.createGrid(origin=origin, latDistance=latDistance, longDistance=longDistance,
                                  adjustedMeridianDistance=1, adjustedParallelDistance=1)

#The following short block of code is a representatation of how these functions should work together.
#functions such as containsSensor, sensorMaxCoords, sensorLocationsDict, and averageActualRSSI are all used as
#subfunctions to the following block
coords_array = gl.makeCoordsArray(latList, longList) # makes 2D array with all lat/long
grid_corners = gl.getGridCorners(coords_array) # stores the corner coordinates of all grid squares
emitter_coords = gl.getEmitterCoords(df500) # finds the coordinates of the all emitters
emitter_locs = gl.getEmitterPositions(emitter_coords, latList, longList, grid_corners) # gets the location of emitters with in the grid
grid = gl.makeGridFanchen(grid_corners, latList, longList, emitter_locs, df500) # creates grid composed of GridSquare objects
#distance_error_array = gl.localizationTest(grid, df500, emitter_locs)


#Print out all the positions that have an emitter in it
#get all grid locations that have an emitter in it
activeEmitters = gl.getActiveEmitterLocs(emitter_locs=emitter_locs)
print("showing active emitters in the grid")
print(activeEmitters)
# Runs localization for Fanchen's dataset on 100 random rows
localizationList, errorList, t = gl.localizationTest(grid, df500, emitter_locs)

# --------------------------------------------------------------------------------
# locating single emitter position

# Runs localization for Fanchen's dataset

# to localize a specific position: ref_sensor 57 and x = 0 for example....
df = df500.loc[(df500['ref_sensor'] == 54) & (df500['x'] == 0.0)]

localizationList, errorList, t = gl.localizationTest(grid, df, activeEmitters)

# calls clustering, [] is for mini_grid as we have no mini-grid here
# USE THIS FOR A SINGLE EMITTER POSITION
# you could technically use it for random, but there is no point to it
# using ref_sensor = 57 and x = 0, true location is (13, 57)
start_loc = gl.clusterLocalization(localizationList, grid, [], (13, 57))

mini_grid, mini_loc, mini_results = gl.mini_grid(grid, start_loc, df) # creates mini_grid

# calls cluster function again to get final "best" guess
cluster = gl.clusterLocalization(mini_loc, grid, mini_grid,
                            gl.getDeviceGridSpot(gl.adjustedLongitude(tl.getCoordinates('54'), 0),
                                                        latList, longList, grid_corners))

grid_loc = gl.getDeviceGridSpot(mini_grid[cluster].center, latList, longList, grid_corners)
print(f'Best guess is at {cluster} in mini-grid and {grid_loc} in full-size grid with actual loc at (13, 57)')
print(f'Final distance error was {round(distance.distance(mini_grid[cluster].center, grid[(13, 57)].center).meters, 2)} meters')

# --------------------------------------------------------------------------------
print()
print()

print("Showing all locations that have a sensor in it")
for i in range(len(grid)):
    for j in range(len(grid[i])):
        tile = grid[i][j]
        if tile.hasSensor:
            print(tile.location)


# The following block demonstrates the gridLocalization function
# For now, it outputs a single tuple representing a cell of the grid
#estimated_device_loc = gl.gridLocalization(grid, df500, emitter_locs)
#print(estimated_device_loc)

#export grid as csv
gl.exportGridAsCsv(grid=grid, pathName="datasets/GridLibDriverGrid.csv", withIndex=True)

# #localizing csv file
#This function will not work right now because we now have a list of data
#we need to put in a csv file. So needs to be updated to take
#localizationlist and write all data from it
csvFile = "datasets/GridLibDriverGrid.csv"
testOutput = "datasets/GridLibDriverGridWithLocalization.csv"
#gl.localizecsv(csvFilePath=csvFile, 
#               csvOutputFilePath=testOutput,
#               localizationData=localizationList)
# gives error so I am commenting out to let rest run


#converting localized csv file to json file
csvFile = "datasets/GridLibDriverGridWithLocalization.csv"
jsonPath = "webDevelopmentFiles/interactiveGrid/grid_json.json"
gl.csvTojson(csvFile, jsonPath)

#showing how multipleGrids works
#origin, latDist, longDist, meridian, parallel
grid0 = [c.GRID_BLOCK_500_ORIGIN, 170, 25, 1, 1]
grid1 = [c.GRID_BLOCK_400_ORIGIN, 140, 25, 1, 1]
grid2 = [c.GRID_BLOCK_300_ORIGIN, 162, 25, 1, 1]
grid3 = [c.GRID_BLOCK_200_ORIGIN, 115, 25, 1, 1]
listOfGrids = [grid0, grid1, grid2, grid3]

m = gl.multipleGrids(listOfGrids=listOfGrids, parentOrigin=c.GRID_BLOCK_400_ORIGIN)
gl.showGrid(m=m, filePath='media/maps/concatMap.html')
# FANCHEN GRID END
# ----------------------------------------------------




# ----------------------------------------------------
# MOBINTEL VERSION OF GRID STUFF

# use datasets\1678683600000-sensor_1.parquet and datasets\1678683600000-sensor_10.parquet
# as example inputs 
print()
print()
all_data = dfl.dataInitialization() # reads, filters, and reorganizes raw MobIntel data

origin, LAT_DIST, LONG_DIST = gl.getGridDimensions(all_data) # calculates origin, length, width of grid
latList , longList = gl.createGrid(origin, LONG_DIST, LAT_DIST, 1, 1) # gets all lats/longs in grid

coords_array = gl.makeCoordsArray(latList, longList) # makes 2D array with all lat/long
print("coords:", coords_array.shape)
grid_corners = gl.getGridCorners(coords_array) # stores the corner coordinates of all grid squares
print("grid_corners:", grid_corners.shape)
grid = gl.makeGridMI(grid_corners, latList, longList, all_data) # creates grid composed of GridSquare objects

# runs localization
loc_list = gl.runLocalizationMI(grid, all_data, grid_corners)

# calls clustering
start_loc = gl.clusterLocalizationMI(loc_list, grid)

# BE AWARE!!!!  ---------------------------------------
# depending on what you want done in gridLocalization, you might have to change
# what dataframe you pass here. For example, if you want to limit localizations 
# to a specific probingtime, you would have to do the same here, since mini_grid
# calls gridLocalization, but not runLocalization where you probably would 
# have done that filtering. 
mini_grid, mini_locs = gl.mini_gridMI(grid, start_loc, all_data) # creates mini_grid
# -----------------------------------------------------

# calls cluster function again to get final "best" guess
cluster = gl.clusterLocalizationMI(mini_locs, grid)

# finds "best" guess location in relation to full-size grid 
# having both mini-grid with grid_corners rather than mini_grid_corners is necessary
# to find the location in the full-size grid  
grid_loc = gl.getDeviceGridSpot(mini_grid[cluster].center, latList, longList, grid_corners)

if grid_loc != -1:
  print(f'Best guess is at {cluster} in mini-grid and {grid_loc} in full-size grid')
else:
  print(f'Best guess is at {cluster} in mini-grid')
  print(f'Not found in full-size grid, but it is located at {mini_grid[cluster].center}')

# MOBINTEL END
# ----------------------------------------------------

"""
This file will attempt to figure out why some probe requests performed
better than others in the graph that phillip has made
"""
import sys
import pandas as pd, numpy as np

sys.path.append("pythonFiles")

from Functionality import GridLib as gl

df500 = pd.read_csv("datasets/block_500_only.csv", engine='python')
df500 = df500.drop(columns=("Unnamed: 0"))
origin = (26.713378, -80.05693981171936)


latList, longList = gl.createGrid(origin=origin, latDistance=25, longDistance=5,
                                  adjustedMeridianDistance=1, adjustedParallelDistance=1)


#The following short block of code is a representatation of how these functions should work together.
#functions such as containsSensor, sensorMaxCoords, sensorLocationsDict, and averageActualRSSI are all used as
#subfunctions to the following block
coords_array = gl.makeCoordsArray(latList, longList) # makes 2D array with all lat/long
grid_corners = gl.getGridCorners(coords_array) # stores the corner coordinates of all grid squares
emitter_coords = gl.getEmitterCoords(df500) # finds the coordinates of the all emitters
emitter_locs = gl.getEmitterPositions(emitter_coords, latList, longList, grid_corners) # gets the location of emitters with in the grid
grid = gl.makeGrid(grid_corners, latList, longList, emitter_locs, df500) # creates grid composed of GridSquare objects
distance_error_array, distance_error_df = gl.localizationTest(grid, df500, emitter_locs)


print("showing distance error array")
print(distance_error_array)

print("Showing distance error array")
print(distance_error_df)

#median is 5.39
median = np.median(distance_error_array)
print(f"The median is {median}")


belowMeanDf = distance_error_df.query("distance_error <= @median")

aboveMeanDf = distance_error_df.query("distance_error > @median")

print("Showing belowMeanDf")
print(belowMeanDf)
print(len(belowMeanDf))
print("Showing aboveMeanDf")
print(aboveMeanDf)
print(len(aboveMeanDf))
#The count of each of these df is about the same, and that makes sense because the median is 
#suppose to be the middle point of the total data.
#but why do have some probe requests with a distance error of 20 meters?

above20ErrorDf = distance_error_df.query("distance_error >= 20")
print("above 20 m distance error group")
print(above20ErrorDf)
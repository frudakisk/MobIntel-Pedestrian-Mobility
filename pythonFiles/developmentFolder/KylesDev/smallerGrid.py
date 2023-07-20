import sys, pandas as pd
sys.path.append('pythonFiles')

import Functionality.GridLib as gl #This import works, but i do not know why there is a problem reported
#reports  reportMissingImports error but the code runs successfully

df500 = pd.read_csv("datasets/block_500_only.csv", engine='python')
origin = (26.713378, -80.05693981171936)
latList, longList = gl.createGrid(origin=origin, latDistance= 25, longDistance= 5, 
              adjustedMeridianDistance= 0.5,
              adjustedParallelDistance= 0.5)

m = gl.visualizeGrid(origin=origin, lat_dist=25, long_dist=5,
                 meridianDist=0.5, parallelDist=0.5)

#gl.showGrid(m, "media/maps/smallerGrid.html")

grid = gl.completeGrid(latList, longList, df500)
print(grid)
for i in range(len(grid)):
    for j in range(len(grid[i])):
        tile = grid[i][j]
        if tile.hasSensor:
            print(tile.location)
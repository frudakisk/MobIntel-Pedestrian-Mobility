"""
This file will attempt to see if there is a clustering of localized points.
If there is such a clustering, we should try to find its focal point and
then we can see if that focal point is close to the original point of the
emitting device

This file will basically just produce a csv file that can be analyzed
in a different file. THis is because producing the new csv file can
take a while since we are going through a very large grid
"""
import sys, pandas as pd, numpy as np

sys.path.append("pythonFiles")

from Functionality import GridLib as gl, Constants as c

df = pd.read_csv("datasets/JoseData.csv")
df500 = pd.read_csv("datasets/block_500_only.csv")

origin = c.GRID_170x25_ORIGIN
grid170x25Tuple = gl.completeGrid(origin= origin,
                latDistance= 170,
                longDistance= 25,
                adjustedMeridianDistance= 1,
                adjustedParallelDistance= 1,
                df500= df500)

grid = grid170x25Tuple[0]

#Step 1: slightly modify JoseData.csv to get only data from one tx_coord location.
#Should result in around 900 rows of data

tx_coord = str((17, 58))
sub_df = df.query("tx_coord == @tx_coord").copy()
print(sub_df)

#Step 2: For each row, calculate the "most likely" localized tile spot and add it as a column in df
#each row should be an emitter location, which it is in this data frame

data = []
sub_df.apply(lambda row: gl.generateLocalizationGuesses(row=row, grid=grid, numberOfGuesses=1, data=data), axis=1)
#now turn data into a dataframe
updatedDf = pd.DataFrame(data)


print("should have new column for best guesses")
print(updatedDf)

#Step 2.5: save results in a csv file so that we don't have to wait for it to compile everytime we are testing something
updatedDf.to_csv("datasets/receiversWithBestLocalization(17,58).csv", index=False)

#Step 3: Count unique localized tile spots. See if there is an obvious clustering pattern
countList = list()
uniqueLocalizationTiles = updatedDf["best_tile_localization"].unique()
for tile in uniqueLocalizationTiles:
    l = [tile, len(updatedDf.query("best_tile_localization == @tile"))]
    countList.append(l)

countList.sort(reverse=True, key=lambda x:x[1])
for item in countList:
    print(item)

#Step 4: If there is some sort of clustering pattern, determine how tight the cluster should be and/or find the middle of the cluster

#There is no need to see how tight they are because we are given single spots as "clusters" but some just have more weight to them


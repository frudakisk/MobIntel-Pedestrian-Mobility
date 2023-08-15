"""
This file will analyze the results of clusteringLocalizedGuesses.py
We will look at the two csv files that were produced and see if there
is any clustering we can easily see.
We will also try to graph any results that we find
"""
import sys, pandas as pd, matplotlib.pyplot as plt, math

sys.path.append("pythonFiles")
from Functionality import GridLib as gl

df = pd.read_csv("datasets/receiversWithBestLocalization(17,58).csv")
df_71 = pd.read_csv("datasets/receiversWithBestLocalization(7,1).csv")

print(df)




def countUniqueLocalizedTiles(df):
    """
    df: should be a receiverWithBestLocalization csv file 
    Returns: A list of lists in the form [(tile_location), count] where we 
    have the localized tile and the amount of times it appeared in the
    best_tile_localization column
    Description: This function finds the unique values in the best_tile_localization
    and then counts how many times each unique value appears. A list of lists is returned
    that contains this information
    """
    countList = list()
    uniqueLocalizationTiles = df["best_tile_localization"].unique()
    for tile in uniqueLocalizationTiles:
        l = [tile, len(df.query("best_tile_localization == @tile"))]
        countList.append(l)

    countList.sort(reverse=True, key=lambda x:x[1])
    return countList

def calculateDistanceError(df, countList):
    """
    df:
    Returns: dataframe with tx_coord, best_tile_localization, and distance Error
    calculate the euclidian distance between the tx_coord and the best_tile_localization.
    produce a list that has these two coords and the distance error
    """
    data = []
    uniqueLocalizationTiles = df["best_tile_localization"].unique()
    originalTileLocation = df.iloc[0]["tx_coord"]
    for tile in uniqueLocalizationTiles:
        for item in countList:
            if tile == item[0]:
                count = item[1]
        distanceError = math.dist(eval(tile), eval(originalTileLocation))
        row = {"tx_coord":originalTileLocation, "best_tile_localization":tile, "distance_error":distanceError, "count": count}
        data.append(row)
    return pd.DataFrame(data)



#main ---------
countList = countUniqueLocalizedTiles(df)
for item in countList:
    print(item)

x = list()
#multiply the item[0] by item[1] and add that to a list
for item in countList[:10]:
    l = [item[0]] * item[1]
    x = x + l #concatinating results


plt.hist(x=x, ec='red')
plt.title(f"(TOP 10) Count of how many times a tile was chosen as best localization prediction for {df.iloc[0]['tx_coord']}")
plt.xlabel("Localized Tile")
plt.ylabel("Count")
plt.show()

test = calculateDistanceError(df, countList)
print("Showing the distance error between the original tile location and all its unique tile localization guesses")
test = test.sort_values(by="distance_error")
print(test.to_string())

test.to_csv("datasets/(17,58)(170x25)localizationClusteringData.csv")

#so far I have only tested (17,58). I should test location (7,1) to see what that df looks like too

countList = countUniqueLocalizedTiles(df_71)
x = list()
for item in countList[:10]:
    l = [item[0]] * item[1]
    x = x + l

plt.hist(x=x, ec='orange')
plt.title(f"(TOP 10) Count of how many times a tile was chosen as best localization prediction for {df_71.iloc[0]['tx_coord']}")
plt.xlabel("Localized Tile")
plt.ylabel("Count")
plt.show()

test = calculateDistanceError(df_71, countList)
test = test.sort_values(by="distance_error")
print(test.to_string())

test.to_csv("datasets/(7,1)(170x25)localizationClusteringData.csv")

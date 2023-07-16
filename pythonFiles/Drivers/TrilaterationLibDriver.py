import sys, pandas as pd
sys.path.append("pythonFiles")

from Functionality import TrilaterationLib as tl

df = pd.read_parquet(path="datasets/fanchen_trilateration_2022_11_13.parquet")
print(df)

#Testing jPrint
print("testing jprint \n")
tl.jprint()

#Testing isSingleDigit
print("\ntesting isSingleDigit\n")
print(tl.isSingleDigit("06"))
print(tl.isSingleDigit(80))
print(tl.isSingleDigit("5"))
print(tl.isSingleDigit("99"))
print(tl.isSingleDigit(1))
print(tl.isSingleDigit(5.12))
print(tl.isSingleDigit(9.9))

print("\ntesting getEmitterCoords(row)\n")
row = df.iloc[0]
rowCoords = tl.getEmitterCoords(row)
print("Retrieved Coordinates of emitter when ref sensor is " + str(int(row["ref_sensor"])) + 
      " and eastern distance from ref sensor is "+ str(row['x']) + ": " + str(rowCoords))

print("\nTesting getCoordinates\n")
print(tl.getCoordinates("s57"))
print(tl.getCoordinates(57))
print(tl.getCoordinates("57"))
print(tl.getCoordinates("06"))
print(tl.getCoordinates("6"))
print(tl.getCoordinates("006"))

print("\nUsing plotRowOnMap with only one row of data\n")
tl.createTrilateratedMap(df=df, headCount=1, centralPoint=tl.getCoordinates("57"), 
                         pathName="media/maps/SingleTrilateratedPoint.html")

#You can also create a subset of data however big or small and plot those points
print("\nUsing plotRowOnMap with subset of dataframe\n")
tl.createTrilateratedMap(df=df, headCount=1000, centralPoint=tl.getCoordinates("57"), d=5, 
                         createCsv=False, oldVersion=False, pathName="media/maps/TrialterationLibDriverMap.html")


print("""Trilateration is used in the plotRowOnMap function, so there is no need to test\n
      the actual functionality of the trilaterate function because its only purpose is in mapping""")



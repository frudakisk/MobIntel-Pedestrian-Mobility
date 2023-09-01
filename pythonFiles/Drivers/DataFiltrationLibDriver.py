import sys, pandas as pd
sys.path.append("pythonFiles")

from Functionality import DataFiltrationLib as dfl

filename = "datasets/1678683600000-sensor_1.parquet"
fanchenFile = "datasets/RSSI_localization_data_WPB/2022_11_08.csv"
df500 = pd.read_csv("datasets/block_500_only.csv")

df = dfl.read_file(filename)
print(df)

df = dfl.sensor_trim(df)
print(df)

df1 = dfl.mac_count(pqfile=df, cutoff=1000)
print(df1)

df = dfl.groupByMacHash(df)
#you must have a dataframe in the form of the one above or else newDetermineDuration will blow up
df["Duration"] = df.apply(lambda row : dfl.newDetermineDuration(row, 7), axis=1)
print(df)

#to make things easier, and cause less error, I have combined the two above functions into one function
#This function utilizes deviceInSensorAreaDuration. This should give the same output as the print statement
#right after applying the lambda function
df = dfl.determineMacHashDuration(filename)
print(df)
df.to_csv("datasets/machashDuration.csv")

subset = dfl.getSubsetByRefSensorAndX(blockDataFrame=df500, refSensor=22, x=0)
print("showing the subset of data taken from df500")
print(subset)


df500, df400 = dfl.convertFanchen(fanchenFileName=fanchenFile)
print(df500)

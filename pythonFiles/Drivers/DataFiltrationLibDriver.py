import sys, pandas as pd
sys.path.append("pythonFiles")

from Functionality import DataFiltrationLib as dfl

filename = "datasets/1678683600000-sensor_1.parquet"
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

#to make things easier, and cause less error, I have combined the two into one function

df = dfl.determineMacHashDuration(filename)
print(df)

subset = dfl.getSubsetByRefSensorAndX(refSensor=22, x=0)
print("showing the subset of data taken from df500")
print(subset)
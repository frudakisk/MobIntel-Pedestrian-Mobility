import sys

sys.path.append('pythonFiles')

import pandas as pd

df = pd.read_csv('datasets/JoseData.csv')

print(df.query("tx_coord == 'NaN'"))

print(df["tx_coord"])

for value in df["tx_coord"]:
    if "(" not in str(value):
        print(value)
        print(type(value))

print("checking if there are any nans")
print(df[df['tx_coord'].apply(lambda x: isinstance(x, float))])

file = "datasets/block_500_only.csv"
df500 = pd.read_csv(file)

print(df500["ref_sensor"].unique())


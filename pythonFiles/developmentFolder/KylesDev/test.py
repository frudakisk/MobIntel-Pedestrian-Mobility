import sys

sys.path.append('pythonFiles')

import pandas as pd
from Functionality import GridLib as gl
from Functionality import PathLossLib as pl

# gl.csvTojson(csvFilePath='datasets/170x25LargeGrid.csv', 
#              jsonPath='webDevelopmentFiles/interactiveGrid/170x25LargeGrid_json.json',
#              removeIndex=False)

df = pd.read_parquet("datasets/fanchen_trilateration_2022_11_13.parquet")
print(df)

df= pd.read_parquet("datasets/1678683600000-sensor_1.parquet")
print(df)

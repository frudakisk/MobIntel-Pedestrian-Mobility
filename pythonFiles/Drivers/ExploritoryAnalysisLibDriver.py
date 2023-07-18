import sys, pandas as pd

sys.path.append("pythonFiles")

from Functionality import ExploritoryAnalysisLib as el

filename = "datasets/1678683600000-sensor_1.parquet"

s = el.rssiSet()
print(s)

dateAgg = el.dateAggDf(filename=filename)
hourAgg = el.hourAggDf(filename=filename)

print(dateAgg)
print(hourAgg)

el.plotDateAgg(dateAgg)
el.plotInDepthWeek(dateAgg, hourAgg)
el.plotDays(dateAgg, hourAgg)
"""
This file will create a 170x25 grid over block 500 of clematis street
I will also plot all the sensors that are on block 500 in this grid
by using the waypoint functionality of the folium library
"""
import sys

sys.path.append("pythonFiles")

from Functionality import GridLib as gl, TrilaterationLib as tl
import folium as f

sensorList = [22, 35, 42, 31, 33, 36, 57, 20, 40, 54, 34]
sensorCoordinates = {}
for sensor in sensorList:
    coordinate = tl.getCoordinates(sensorNum=sensor)
    sensorCoordinates[sensor] = coordinate

print(sensorCoordinates)

origin = (26.71333451697524, -80.05695531266622)
m = gl.visualizeGrid(origin=origin,
                     lat_dist=170,
                     long_dist=25,
                     meridianDist=1,
                     parallelDist=1)

for key, value in sensorCoordinates.items():
    sensorStr = f"Sensor: {key}"
    f.Marker(location=value, tooltip="click me!", popup=sensorStr).add_to(m)

gl.showGrid(m=m, filePath="media/maps/170x25LargeGridMapWithSensors.html")
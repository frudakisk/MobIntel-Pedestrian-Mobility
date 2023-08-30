"""
This file will create routes for the user to follow when creating
data for trajectory stuff. This is just testing, nothing concrete.
"""
import folium, webbrowser, sys
from geopy import distance

sys.path.append("pythonFiles")

from Functionality import GridLib as gl
#constants for this file
mapOrigin = (26.71340627235558, -80.05629962597477)
checkpoint1 = (26.713407470318927, -80.05691519291247)
checkpoint2 = (26.713407470318927, -80.0562557527166)
checkpoint3 = (26.71349072873813, -80.05625268729479)
checkpoint4 = (26.713486535869457, -80.0556223682082)

#create a map
m = folium.Map(location=mapOrigin, width=2000, height=900, zoom_start=19, max_zoom=21)
#gather constant coordinates so that we can save them as checkpoints
#connect the checkpoints with straight lines
folium.PolyLine(locations=[checkpoint1, checkpoint2]).add_to(m)
folium.PolyLine(locations=[checkpoint2, checkpoint3]).add_to(m)
folium.PolyLine(locations=[checkpoint3, checkpoint4]).add_to(m)

#mark checkpoints
folium.Marker(location=checkpoint1, popup=checkpoint1).add_to(m)
folium.Marker(location=checkpoint2, popup=checkpoint2).add_to(m)
folium.Marker(location=checkpoint3, popup=checkpoint3).add_to(m)
folium.Marker(location=checkpoint4, popup=checkpoint4).add_to(m)

#show the map
m.save("media/maps/route.html")
webbrowser.open("media/maps/route.html", new=2)

#what is the distance between each of these checkpoints
d = distance.distance(checkpoint1, checkpoint2).meters
print(d)
d = distance.distance(checkpoint2, checkpoint3).meters
print(d)
d = distance.distance(checkpoint1, checkpoint3).meters
print(d)

newD = gl.adjustedLongitude(checkpoint1, 65.5)
print(newD)
d = distance.distance(checkpoint1, newD).meters
print(d)
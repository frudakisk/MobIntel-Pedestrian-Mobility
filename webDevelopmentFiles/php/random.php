<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>Generate a random walk on Google Maps</title>
<script async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCgWmMXzXgQDF3qai4VUz5Kxn07kBY9hsM&callback=initMap&libraries=geometry,places" type="text/javascript"></script>
<style>
/* Always set the map height explicitly to define the size of the div
 * element that contains the map. */
#map {
     height: 100%;
}

/* Optional: Makes the sample page fill the window. */
html, body {
     height: 100%;
     margin: 0;
     padding: 0;
}

.slidecontainer {
     width: 100%;
}

.slider {
     -webkit-appearance: none;
     width: 100%;
     height: 25px;
     background: #669699;
     outline: none;
     opacity: 0.7;
     -webkit-transition: .2s;
     transition: opacity .2s;
}

.slider:hover {
     opacity: 1;
}

.slider::-webkit-slider-thumb {
     -webkit-appearance: none;
     appearance: none;
     width: 25px;
     height: 25px;
     background: #f70508;
     cursor: pointer;
}

.slider::-moz-range-thumb {
     width: 25px;
     height: 25px;
     background: #f70508;
     cursor: pointer;
}

#controls {
     width: 15%;
     background-color: #f5f5f0;
     margin: 5px;
     padding: 5px;
     border-radius: 15px;
     opacity: 0.85;
}

.info {
     width: 40%;
     font-size: 18px;
}

@media only screen and (min-device-width: 300px) and (max-device-width: 1024px) and (orientation:portrait) {
  #controls {
       width: 35%;
       background-color: #f5f5f0;
       margin: 5px;
       padding: 5px;
       border-radius: 15px;
       opacity: 0.85;
  }

  .info {
       width: 95%;
       font-size: 40px;
  }

  #placeInput {
    font-size: 45px;
  }

  #recreateRoute {
    font-size: 45px;
  }
}
</style>
</head>

<body>
<div id="controls">
  <div class="slidecontainer">
    <input type="range" min="500" max="5000" value="2000" step="500" class="slider" id="myRange" style="95%">
    <p class="info">Range: <span id="demo" style="float: right;"></span></p>
  </div>
  <div class="slidecontainer">
    <input type="range" min="1" max="20" value="5" class="slider" id="waypointsRange">
    <p class="info">Waypoints: <span id="waypointsValue" style="float: right;"></span></p>
  </div>
  <input id="placeInput" type="text" placeholder="Post Code" style="width: 95%; display: block;">
  <button id="recreateRoute" onclick="placesChanged()" style="display: none">Recreate</button>
</div>
<!--The div element for the map -->
<div id="map"></div>
<!-- Replace the value of the key parameter with your own API key. -->
<script type="text/javascript">
var directionsService;
var directionsRenderer;
var markers;
var searchBox;
var map;
var restrictionsCircle;
var rangeCircle;
var slider = document.getElementById("myRange");
var waypointsRange = document.getElementById("waypointsRange");
var output = document.getElementById("demo");
var waypointsValue = document.getElementById("waypointsValue");
var input = document.getElementById("placeInput");
var recreateRoute = document.getElementById("recreateRoute");

var waypointMarkers = 5;
var radius = 2000;
var maxRadius = 5000;

output.innerHTML = (slider.value / 1000).toFixed(1) + "km";
waypointsValue.innerHTML = waypointsRange.value;

slider.oninput = function() {
    output.innerHTML = (this.value / 1000).toFixed(1) + "km";
    radius = parseInt(this.value, 10);
}

waypointsRange.oninput = function() {
    waypointsValue.innerHTML = this.value;
    waypointMarkers = parseInt(this.value, 10);
}

// Initialize and add the map
function initMap() {
    directionsService = new google.maps.DirectionsService;
    directionsRenderer = new google.maps.DirectionsRenderer;

    // home latitude/longitude
    var home = {
        lat: 26.712979,
        lng: -80.049997
    };
    // The map, centered at home
    var mapElement = document.getElementById('map');
    map = new google.maps.Map(mapElement, {
        zoom: 18,
        center: home
    });

    var controls = document.getElementById('controls');
    searchBox = new google.maps.places.SearchBox(input);
    map.controls[google.maps.ControlPosition.LEFT_CENTER].push(controls);
    // Bias the SearchBox results towards current map's viewport.
    map.addListener('bounds_changed', function() {
        searchBox.setBounds(map.getBounds());
    });

    directionsRenderer.setMap(map);
    markers = [];

    searchBox.addListener('places_changed', placesChanged);
}

function placesChanged() {
    input.style.display = 'none'
    recreateRoute.style.display = 'block';

    var places = searchBox.getPlaces();

    if (places.length == 0) {
        return;
    }

    // Clear out the old markers.
    markers.forEach(function(marker) {
        marker.setMap(null);
    });
    markers = [];


    // For each place, get the icon, name and location.
    var bounds = new google.maps.LatLngBounds();
    places.forEach(function(place) {
        home = place.geometry.location;
        if (!place.geometry) {
            console.log("Returned place contains no geometry");
            return;
        }
        var icon = {
            url: place.icon,
            size: new google.maps.Size(71, 71),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(17, 34),
            scaledSize: new google.maps.Size(25, 25)
        };
        // Create a marker for each place.
        markers.push(new google.maps.Marker({
            map: map,
            icon: icon,
            title: place.name,
            position: place.geometry.location
        }));

        if (restrictionsCircle) {
            restrictionsCircle.setMap(null);
        }
        restrictionsCircle = new google.maps.Circle({
            strokeColor: '#990000',
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: '#CC000',
            fillOpacity: 0.1,
            map: map,
            center: home,
            radius: maxRadius
        });
        if (rangeCircle) {
            rangeCircle.setMap(null);
        }
        // A circle, with a radius defined by the slider, centered at home
        rangeCircle = new google.maps.Circle({
            strokeColor: '#FF0000',
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: '#FF0000',
            fillOpacity: 0.05,
            map: map,
            center: home,
            radius: radius
        });

        // Position a marker at home
        var marker = new google.maps.Marker({
            position: home,
            map: map
        });
        // Array of waypoints
        var waypoints = [];

        var degreesInCircle = 360;
        var increase = degreesInCircle / waypointMarkers;
        for (var bearing = 0; bearing < degreesInCircle; bearing += increase) {

            // Distance is a random number at most 2000m (2km) from home
            var distanceFromHome = Math.random() * radius;
            // Calculate a point on the map, at a random distance from home
            // within the 2km radius
            var waypoint = google.maps.geometry.spherical.computeOffset(marker.getPosition(), distanceFromHome, bearing);
            // Push a new waypoint to the array
            waypoints.push({
                location: waypoint,
                stopover: true
            });
            bounds.extend(waypoint);
        }

        // Calculate a walking route from home to home,
        // with the waypoints created above
        directionsService.route({
            origin: marker.getPosition(),
            destination: marker.getPosition(),
            waypoints: waypoints,
            optimizeWaypoints: true,
            travelMode: 'WALKING',
            avoidHighways: true
        }, function(response, status) {
            if (status === 'OK') {
                console.log('Directions created');
                directionsRenderer.setDirections(response);
            } else {
                window.alert('Directions request failed due to ' + status);
            }
        });
    });
    map.fitBounds(bounds);
}
</script>
</body>
</html>

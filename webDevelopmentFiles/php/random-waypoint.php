<?php
/**
 * This file is a random waypoint model simulation, it creates a trajectory between two coordinates by selecting
 * sensor coordinates as waypoints. The selection of waypoints is based on the density of detected probes at the selected time.
 * It takes as parameters a starting coordinate, and ending coordinate and the speed as meters per move and two date times.
 */

/**
 * this is just for backwards compatibility with old php versions.
 */
if (! function_exists("array_key_last")) {
    function array_key_last($array) {
        if (!is_array($array) || empty($array)) {
            return NULL;
        }

        return array_keys($array)[count($array)-1];
    }
}

// array of all sensors, same list from the MobIntel API.
$sensors = array(
//    array(
//        'sensorId' => 17,
//        'location' =>
//            array(
//                'x' => 26.713254,
//                'y' => -80.051483,
//            ),
//        'label' => 'Sensor 18',
//    ),
//    array(
//        'sensorId' => 18,
//        'location' =>
//            array(
//                'x' => 26.713241,
//                'y' => -80.051114,
//            ),
//        'label' => 'Sensor 19',
//    ),
//    array(
//        'sensorId' => 16,
//        'location' =>
//            array(
//                'x' => 26.713377,
//                'y' => -80.051308,
//            ),
//        'label' => 'Sensor 17',
//    ),
//    array(
//        'sensorId' => 36,
//        'location' =>
//            array(
//                'x' => 26.71324,
//                'y' => -80.051,
//            ),
//        'label' => 'Sensor 48',
//    ),
//    array(
//        'sensorId' => 23,
//        'location' =>
//            array(
//                'x' => 26.713438,
//                'y' => -80.05368,
//            ),
//        'label' => 'Sensor 21',
//    ),
//    array(
//        'sensorId' => 20,
//        'location' =>
//            array(
//                'x' => 26.713333,
//                'y' => -80.053663,
//            ),
//        'label' => 'Sensor 25',
//    ),
//    array(
//        'sensorId' => 22,
//        'location' =>
//            array(
//                'x' => 26.71332,
//                'y' => -80.053839,
//            ),
//        'label' => 'Sensor 27',
//    ),
//    array(
//        'sensorId' => 35,
//        'location' =>
//            array(
//                'x' => 26.713175,
//                'y' => -80.050499,
//            ),
//        'label' => 'Sensor 32',
//    ),
//    array(
//        'sensorId' => 32,
//        'location' =>
//            array(
//                'x' => 26.713336,
//                'y' => -80.050887,
//            ),
//        'label' => 'Sensor 43',
//    ),
//    array(
//        'sensorId' => 37,
//        'location' =>
//            array(
//                'x' => 26.713369,
//                'y' => -80.051099,
//            ),
//        'label' => 'Sensor 47',
//    ),
//    array(
//        'sensorId' => 34,
//        'location' =>
//            array(
//                'x' => 26.713217,
//                'y' => -80.050585,
//            ),
//        'label' => 'Sensor 44',
//    ),
//    array(
//        'sensorId' => 33,
//        'location' =>
//            array(
//                'x' => 26.713371,
//                'y' => -80.05057,
//            ),
//        'label' => 'Sensor 45',
//    ),
//    array(
//        'sensorId' => 38,
//        'location' =>
//            array(
//                'x' => 26.713247,
//                'y' => -80.050775,
//            ),
//        'label' => 'Sensor 46',
//    ),
//    array(
//        'sensorId' => 9,
//        'location' =>
//            array(
//                'x' => 26.713267,
//                'y' => -80.052031,
//            ),
//        'label' => 'Sensor 10',
//    ),
//    array(
//        'sensorId' => 15,
//        'location' =>
//            array(
//                'x' => 26.713384,
//                'y' => -80.051707,
//            ),
//        'label' => 'Sensor 16',
//    ),
//    array(
//        'sensorId' => 41,
//        'location' =>
//            array(
//                'x' => 26.713292911204316,
//                'y' => -80.05294297087231,
//            ),
//        'label' => 'Sensor 51',
//    ),
//    array(
//        'sensorId' => 42,
//        'location' =>
//            array(
//                'x' => 26.713450632546753,
//                'y' => -80.05415014341882,
//            ),
//        'label' => 'Sensor 50',
//    ),
//    array(
//        'sensorId' => 13,
//        'location' =>
//            array(
//                'x' => 26.713253,
//                'y' => -80.051737,
//            ),
//        'label' => 'Sensor 14',
//    ),
//    array(
//        'sensorId' => 12,
//        'location' =>
//            array(
//                'x' => 26.713383,
//                'y' => -80.051588,
//            ),
//        'label' => 'Sensor 13',
//    ),
//    array(
//        'sensorId' => 11,
//        'location' =>
//            array(
//                'x' => 26.713253,
//                'y' => -80.051599,
//            ),
//        'label' => 'Sensor 12',
//    ),
//    array(
//        'sensorId' => 43,
//        'location' =>
//            array(
//                'x' => 26.713319672370567,
//                'y' => -80.05400151275425,
//            ),
//        'label' => 'Sensor 53',
//    ),
//    array(
//        'sensorId' => 19,
//        'location' =>
//            array(
//                'x' => 26.713422,
//                'y' => -80.050483,
//            ),
//        'label' => 'Sensor 52',
//    ),
//    array(
//        'sensorId' => 21,
//        'location' =>
//            array(
//                'x' => 26.713453,
//                'y' => -80.053955,
//            ),
//        'label' => 'Sensor 08',
//    ),
//    array(
//        'sensorId' => 40,
//        'location' =>
//            array(
//                'x' => 26.713404511344233,
//                'y' => -80.0530895305153,
//            ),
//        'label' => 'Sensor 41',
//    ),
//    array(
//        'sensorId' => 10,
//        'location' =>
//            array(
//                'x' => 26.713259,
//                'y' => -80.052244,
//            ),
//        'label' => 'Sensor 26',
//    ),
//    array(
//        'sensorId' => 45,
//        'location' =>
//            array(
//                'x' => 26.713457,
//                'y' => -80.054317,
//            ),
//        'label' => 'Sensor 07',
//    ),
//    array(
//        'sensorId' => 1,
//        'location' =>
//            array(
//                'x' => 26.713262,
//                'y' => -80.052443,
//            ),
//        'label' => 'Sensor 01',
//    ),
//    array(
//        'sensorId' => 2,
//        'location' =>
//            array(
//                'x' => 26.71327,
//                'y' => -80.052675,
//            ),
//        'label' => 'Sensor 02',
//    ),
//    array(
//        'sensorId' => 3,
//        'location' =>
//            array(
//                'x' => 26.713374,
//                'y' => -80.052445,
//            ),
//        'label' => 'Sensor 03',
//    ),
//    array(
//        'sensorId' => 44,
//        'location' =>
//            array(
//                'x' => 26.713328520319507,
//                'y' => -80.05421610676242,
//            ),
//        'label' => 'Sensor 55',
//    ),
//    array(
//        'sensorId' => 46,
//        'location' =>
//            array(
//                'x' => 26.713341,
//                'y' => -80.054383,
//            ),
//        'label' => 'Sensor 56',
//    ),
//    array(
//        'sensorId' => 48,
//        'location' =>
//            array(
//                'x' => 26.7133409,
//                'y' => -80.054607,
//            ),
//        'label' => 'Sensor 38',
//    ),
    array(
        'sensorId' => 50,
        'location' =>
            array(
                'x' => 26.7133589,
                'y' => -80.0548058,
            ),
        'label' => 'Sensor 39',
    ),
//    array(
//        'sensorId' => 54,
//        'location' =>
//            array(
//                'x' => 26.7134373,
//                'y' => -80.0548008,
//            ),
//        'label' => 'Sensor 11',
//    ),
    array(
        'sensorId' => 57,
        'location' =>
            array(
                'x' => 26.7134448,
                'y' => -80.0545805,
            ),
        'label' => 'Sensor 28',
    ),
    array(
        'sensorId' => 51,
        'location' =>
            array(
                'x' => 26.713367,
                'y' => -80.0557215,
            ),
        'label' => 'Sensor 35',
    ),
    array(
        'sensorId' => 53,
        'location' =>
            array(
                'x' => 26.7134853,
                'y' => -80.0556822,
            ),
        'label' => 'Sensor 34',
    ),
//    array(
//        'sensorId' => 64,
//        'location' =>
//            array(
//                'x' => 26.713508,
//                'y' => -80.056925,
//            ),
//        'label' => 'Sensor 57',
//    ),
//    array(
//        'sensorId' => 31,
//        'location' =>
//            array(
//                'x' => 26.713527,
//                'y' => -80.057113,
//            ),
//        'label' => 'Sensor 23',
//    ),
    array(
        'sensorId' => 52,
        'location' =>
            array(
                'x' => 26.713372,
                'y' => -80.055947,
            ),
        'label' => 'Sensor 36',
    ),
//    array(
//        'sensorId' => 29,
//        'location' =>
//            array(
//                'x' => 26.713406,
//                'y' => -80.057136,
//            ),
//        'label' => 'Sensor 24',
//    ),
    array(
        'sensorId' => 49,
        'location' =>
            array(
                'x' => 26.7133921,
                'y' => -80.0563562,
            ),
        'label' => 'Sensor 31',
    ),
//    array(
//        'sensorId' => 66,
//        'location' =>
//            array(
//                'x' => 26.712979,
//                'y' => -80.049997,
//            ),
//        'label' => 'Sensor 58',
//    ),
//    array(
//        'sensorId' => 56,
//        'location' =>
//            array(
//                'x' => 26.713393,
//                'y' => -80.056127,
//            ),
//        'label' => 'Sensor 33',
//    ),
//    array(
//        'sensorId' => 62,
//        'location' =>
//            array(
//                'x' => 26.713495,
//                'y' => -80.056362,
//            ),
//        'label' => 'Sensor 54',
//    ),
//    array(
//        'sensorId' => 59,
//        'location' =>
//            array(
//                'x' => 26.713479,
//                'y' => -80.055881,
//            ),
//        'label' => 'Sensor 40',
//    ),
//    array(
//        'sensorId' => 63,
//        'location' =>
//            array(
//                'x' => 26.713386,
//                'y' => -80.05654,
//            ),
//        'label' => 'Sensor 42',
//    ),
    array(
        'sensorId' => 61,
        'location' =>
            array(
                'x' => 26.713393,
                'y' => -80.056737,
            ),
        'label' => 'Sensor 06',
    ),
//    array(
//        'sensorId' => 60,
//        'location' =>
//            array(
//                'x' => 26.713499,
//                'y' => -80.056513,
//            ),
//        'label' => 'Sensor 04',
//    ),
    array(
        'sensorId' => 30,
        'location' =>
            array(
                'x' => 26.71351,
                'y' => -80.056714,
            ),
        'label' => 'Sensor 20',
    ),
    array(
        'sensorId' => 28,
        'location' =>
            array(
                'x' => 26.713399,
                'y' => -80.056938,
            ),
        'label' => 'Sensor 22',
    ),
//    array(
//        'sensorId' => 65,
//        'location' =>
//            array(
//                'x' => 26.713475,
//                'y' => -80.050185,
//            ),
//        'label' => 'Sensor 49',
//    ),
//    array(
//        'sensorId' => 47,
//        'location' =>
//            array(
//                'x' => 26.372958,
//                'y' => -80.098605,
//            ),
//        'label' => 'Sensor 37',
//    ),
//    array(
//        'sensorId' => 4,
//        'location' =>
//            array(
//                'x' => 26.7134936,
//                'y' => -80.0561137,
//            ),
//        'label' => 'Sensor 05',
//    ),
//    array(
//        'sensorId' => 14,
//        'location' =>
//            array(
//                'x' => 26.7133933,
//                'y' => -80.052764,
//            ),
//        'label' => 'Sensor 15',
//    ),
);

/**
 * the class creates a random path between sensors and displays it on a map.
 */
class Node
{
    private $latitude;
    private $longitude;
    private $speed;
    public $startLocation;
    public $endLocation;
    public $waypoints = [];
    public $currentWaypointIndex = 0;
    public $current_date;
    private $minLat;
    private $maxLat;
    private $minLng;
    private $maxLng;

    public function __construct($startLocation, $endLocation, $speed, $minLat, $maxLat, $minLng, $maxLng, $initial_date) {
        $this->startLocation = $startLocation;
        $this->endLocation = $endLocation;
        $this->speed = $speed;
        $this->minLat = $minLat;
        $this->maxLat = $maxLat;
        $this->minLng = $minLng;
        $this->maxLng = $maxLng;
        $this->generateWaypoints();
        $this->setInitialLocation();
        $this->current_date = $initial_date;
    }

    // not in use anymore, used before to select a random coordinate, now we use sensor coordinates.
    private function generateRandomCoordinate($min, $max, $decimals = 6) {
        $randomCoordinate = mt_rand() / mt_getrandmax() * ($max - $min) + $min;
        return round($randomCoordinate, $decimals);
    }

    /**
     * selects waypoints from a list of sensors.
     * @return void
     */
    private function generateWaypoints() {
        global $sensors;
        $numWaypoints = mt_rand(9, 9);

    /*    for ($i = 0; $i < $numWaypoints; $i++) {
            $latitude = $this->generateRandomCoordinate($this->minLat, $this->maxLat);
            $longitude = $this->generateRandomCoordinate($this->minLng, $this->maxLng);
            $random_sensor = $sensors[array_rand($sensors, 1)];
            $latitude = $random_sensor['location']['x'];
            $longitude = $random_sensor['location']['y'];
            $this->waypoints[] = ['latitude' => $latitude, 'longitude' => $longitude, 'sensor_id' => $random_sensor['sensorId']];
        }*/

        foreach ($sensors as $sensor) {
            $latitude = $sensor['location']['x'];
            $longitude = $sensor['location']['y'];
            $this->waypoints[] = ['latitude' => $latitude, 'longitude' => $longitude, 'sensor_id' => $sensor['sensorId']];
        }

        $this->make_unique();
        $this->calculateDistances();
        $this->calculateDensities();
        $this->sortWaypoints();

        $this->waypoints[] = $this->endLocation;
    }

    // sets the starting coordinate.
    private function setInitialLocation() {
        $this->latitude = $this->startLocation['latitude'];
        $this->longitude = $this->startLocation['longitude'];
    }

    // Calculates distance between two coordinates.
    public function calculateDistance($latA, $lonA, $latB, $lonB) {
        $earthRadius = 6371; // Earth's radius in kilometers

        $latA = deg2rad($latA);
        $lonA = deg2rad($lonA);
        $latB = deg2rad($latB);
        $lonB = deg2rad($lonB);

        $deltaLat = $latB - $latA;
        $deltaLon = $lonB - $lonA;

        $a = sin($deltaLat / 2) * sin($deltaLat / 2) +
            cos($latA) * cos($latB) *
            sin($deltaLon / 2) * sin($deltaLon / 2);

        $c = 2 * atan2(sqrt($a), sqrt(1 - $a));

        return $earthRadius * $c;
    }

    /**
     * moves to a new coordinate, parameters are selected in constructor.
     * @return void
     */
    public function move() {
        $currentLat = $this->latitude;
        $currentLng = $this->longitude;
        $currentWaypoint = $this->waypoints[$this->currentWaypointIndex];
        $distanceToWaypoint = $this->calculateDistance($currentLat, $currentLng, $currentWaypoint['latitude'], $currentWaypoint['longitude']);
        // Get the current date and time
        $this->current_date->modify('+5 minutes')->format('Y-m-d H:i:s');


        if ($distanceToWaypoint <= $this->speed) {
            // Reached the current waypoint, move to the next one
            $this->currentWaypointIndex++;

            if ($this->currentWaypointIndex >= count($this->waypoints)) {
                // Reached the end location
                $this->latitude = $this->endLocation['latitude'];
                $this->longitude = $this->endLocation['longitude'];
                return;
            }
        }

        $waypointLat = $this->waypoints[$this->currentWaypointIndex]['latitude'];
        $waypointLng = $this->waypoints[$this->currentWaypointIndex]['longitude'];

        $heading = $this->calculateBearing($currentLat, $currentLng, $waypointLat, $waypointLng);
        $distanceToMove = min($this->speed, $distanceToWaypoint);
        $this->calculateDestinationCoordinate($this->latitude, $this->longitude, $distanceToMove, $heading);
    }

    /**
     * adds the density to each waypoint, how many probes are captured between time periods.
     * @return void
     */
    public function calculateDensities() {
        $mysqli = new mysqli('localhost', 'root', 'root', 'trilateration');
        $day_number = 5;
        $start_hour = 3;
        $end_hour = 4;
        foreach ($this->waypoints as $key => $waypoint) {
             $result = $mysqli->query("SELECT COUNT(*) as record_count FROM probes 
              WHERE DAYOFWEEK(probingtime) = {$day_number} AND sensorid = {$waypoint['sensor_id']}
              AND HOUR(`probingtime`) >= {$start_hour} AND HOUR(`probingtime`) <= {$end_hour}");
              $rows = $result->fetch_all(MYSQLI_ASSOC);
              $this->waypoints[$key]['density'] = $rows[0]['record_count'];
        }

        $mysqli->close();
    }

    /**
     * calculates the distance from the starting point to each waypoint.
     * @return void
     */
    public function calculateDistances() {
        foreach ($this->waypoints as $key => $waypoint) {
            $this->waypoints[$key]['distance'] = $this->calculateDistance($this->startLocation['latitude'], $this->startLocation['longitude'], $waypoint['latitude'], $waypoint['longitude']);
        }
    }

    public function calculateDestinationCoordinate($latA, $lonA, $distance, $bearing) {
        $radius = 6371;  // Earth's radius in kilometers

        $latA = deg2rad($latA);
        $lonA = deg2rad($lonA);
        $bearing = deg2rad($bearing);

        $latB = asin(sin($latA) * cos($distance / $radius) + cos($latA) * sin($distance / $radius) * cos($bearing));
        $lonB = $lonA + atan2(sin($bearing) * sin($distance / $radius) * cos($latA), cos($distance / $radius) - sin($latA) * sin($latB));

        $this->latitude = rad2deg($latB);
        $this->longitude = rad2deg($lonB);
    }

    public function calculateBearing($latA, $lonA, $latB, $lonB) {
        $deltaLon = deg2rad($lonB - $lonA);

        $latA = deg2rad($latA);
        $latB = deg2rad($latB);

        $y = sin($deltaLon) * cos($latB);
        $x = cos($latA) * sin($latB) - sin($latA) * cos($latB) * cos($deltaLon);

        $directionRad = atan2($y, $x);
        $directionDeg = rad2deg($directionRad);

        $directionDeg = ($directionDeg + 360) % 360;

        return $directionDeg;
    }

    public function getLocation() {
        return ['latitude' => $this->latitude, 'longitude' => $this->longitude];
    }

    public function make_unique() {
        // Create an associative array with 'field' values as keys
        $uniqueArray = array_reduce($this->waypoints, function($carry, $item) {
            $carry[$item['sensor_id']] = $item;
            return $carry;
        }, []);

        // Get the values from the associative array to remove the keys
        $this->waypoints = array_values($uniqueArray);
    }

    /**
     * sorts waypoints by density, the node moves first to the waypoint with the greater density.
     * @return void
     */
    public function sortWaypoints() {
        usort($this->waypoints, function($a, $b) {
            return ($a['distance'] < $b['distance']) ? -1 : 1;
        });

        usort($this->waypoints, function($a, $b) {
            return ($a['distance'] < $b['distance']) ? -1 : 1;
        });
        var_dump($this->waypoints);
    }
}


function display_map($latitude, $longitude) {
    $coordinates = "|" . $latitude . "," . $longitude;
    echo "<div class='img-block'>";
    echo "<img src='https://maps.googleapis.com/maps/api/staticmap?size=760x400&maptype=roadmap&scale=2&zoom=1\
&markers=size:tiny|color:red{$coordinates}|&key=AIzaSyCgWmMXzXgQDF3qai4VUz5Kxn07kBY9hsM' />";
    // echo "<h2>Time: $time seconds</h2>";
    echo "</div>";
}

?>

<!DOCTYPE html>
<html>
<head>
    <title></title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>
    <script>
      (function ($) {
        $(window).on("load", function () {

          let images = $('.img-block');
          let index = 0;
          $('.js-animation').show();
          const interval = setInterval(function () {
            if (index == images.length) {
              index = 0;
            }
            images.css('opacity', 0);
            images.eq(index).css('opacity', 1);
            console.log(index);
            index++;
          }, 600);


        });
      })(jQuery);
    </script>
    <style>
        body {
            font-family: sans-serif;
        }

        .js-animation {
            display: none;
            height: 900px;
        }

        .img-block {
            position: absolute;
            opacity: 0;
        }

        .img-block:first-child {
            position: absolute;
        }
    </style>
</head>
<body>
<div class="js-animation">
    <?php
    $startLocation = ['latitude' => 26.713406, 'longitude' => -80.057136]; // Sensor 24
    $endLocation = ['latitude' => 26.7133589, 'longitude' => -80.0548058]; // Sensor 39
    $minLatitude = 26.712587999206054;   // Minimum latitude value
    $maxLatitude = 26.71443765287941;    // Maximum latitude value
    $minLongitude = -80.050302; // Minimum longitude value
    $maxLongitude = -80.05782293142235;  // Maximum longitude value
    $speed = 0.01; // kms
    $distanceThreshold = 0.005; // kms
    $initial_date = new DateTime();

    $node = new Node($startLocation, $endLocation, $speed, $minLatitude, $maxLatitude, $minLongitude, $maxLongitude, $initial_date);

    echo "Starting Location: Latitude: " . $node->getLocation()['latitude'] . ", Longitude: " . $node->getLocation()['longitude'] . "\n";
    // var_dump($node->waypoints);

    $waypoints = "";
    $count = 0;
    foreach ($node->waypoints as $key => $waypoint) {
        $waypoints .= "&markers=size:tiny|color:red|" . $waypoint['latitude'] . "," . $waypoint['longitude'];
        if ($key === array_key_last($node->waypoints)) {
            $waypoints .= "&";
        }
        $count++;
//      var_dump($node->calculateDistance($waypoint['latitude'], $waypoint['longitude'], $endLocation['latitude'], $endLocation['longitude']));
    }


    $coordinates = "";
    while ($node->calculateDistance($node->getLocation()['latitude'], $node->getLocation()['longitude'], $endLocation['latitude'], $endLocation['longitude']) > $distanceThreshold) {
        $coordinates .= "|" . $node->getLocation()['latitude'] . "," . $node->getLocation()['longitude'];
        /*error_log("distance: " . $node->calculateDistance($node->getLocation()['latitude'], $node->getLocation()['longitude'], $node->waypoints[$node->currentWaypointIndex]['latitude'], $node->waypoints[$node->currentWaypointIndex]['longitude']));
        error_log("bearing: " . $node->calculateBearing($node->getLocation()['latitude'], $node->getLocation()['longitude'], $node->waypoints[$node->currentWaypointIndex]['latitude'], $node->waypoints[$node->currentWaypointIndex]['longitude']));*/
        display_map_1($coordinates, $waypoints, $node->current_date);
        $node->move();
    }

    /*    for ($node->calculateDistance($node->getLocation()['latitude'], $node->getLocation()['longitude'], $endLocation['latitude'], $endLocation['longitude']) > $distanceThreshold) {
    //        display_map($node->getLocation()['latitude'], $node->getLocation()['longitude']);
            echo "Current location: {$node->getLocation()['latitude']},  {$node->getLocation()['longitude']} <br />";
            echo "Distance between: " . $node->calculateDistance($node->getLocation()['latitude'], $node->getLocation()['longitude'], $endLocation['latitude'], $endLocation['longitude']) . "<br />";
            $node->move();
        }*/

    echo "Reached final destination, end of simulation.";
    ?>
    <?php

    function display_map_1($coordinates, $waypoints, $current_date) {
        global $node;
        $path = $coordinates;
        // &path=color:0x0000ff{$path}
        echo "<div class='img-block'>";
        /*echo "<img src='https://maps.googleapis.com/maps/api/staticmap?size=760x400&maptype=roadmap&scale=2&zoom=1\
    &markers=size:tiny|color:red{$coordinates}&markers=size:tiny|color:blue|26.713406,-80.057136|26.712979,-80.049997|
    &path=color:0x0000ff|weight:5|{$coordinates}|&key=AIzaSyCgWmMXzXgQDF3qai4VUz5Kxn07kBY9hsM' />";*/

       /* echo "<img src='https://maps.googleapis.com/maps/api/staticmap?size=760x400&scale=2&zoom=18
&markers=size:tiny|color:blue|{$node->startLocation['latitude']},{$node->startLocation['longitude']}|{$node->endLocation['latitude']},{$node->endLocation['longitude']}
{$waypoints}markers=size:tiny|color:yellow{$coordinates}
&key=AIzaSyCgWmMXzXgQDF3qai4VUz5Kxn07kBY9hsM'>";
        echo "<h2>Timestamp: {$current_date->format('Y-m-d H:i:s')}</h2>";
        echo "</div>";*/

        // with path instead of markers.
           echo "<img src='https://maps.googleapis.com/maps/api/staticmap?size=760x400&scale=2&zoom=18
       &markers=size:tiny|color:blue|{$node->startLocation['latitude']},{$node->startLocation['longitude']}|{$node->endLocation['latitude']},{$node->endLocation['longitude']}
       {$waypoints}&path=color:0x0000ff{$path}
       &key=AIzaSyCgWmMXzXgQDF3qai4VUz5Kxn07kBY9hsM'>";
           echo "<h2>Timestamp: {$current_date->format('Y-m-d H:i:s')}</h2>";
           echo "</div>";
    }
    ?>
</div>
<form method="post" action="">
    <label for="datetime1">Datetime 1:</label>
    <input type="datetime-local" id="datetime1" name="datetime1"><br><br>

    <label for="datetime2">Datetime 2:</label>
    <input type="datetime-local" id="datetime2" name="datetime2"><br><br>

    <input type="submit" value="Submit">
</form>
</body>
</html>


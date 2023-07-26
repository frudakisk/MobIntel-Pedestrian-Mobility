<?php
/**
 * This file is a random walk model simulation, the first experiment in generating mobility traces,
 * it calculates a new direction and moves the specified distance in that direction, it runs by the specified time.
 * It's all displayed in a map for easy visualization.
 * It takes speed and simulation time as parameters.
 */

class Entity
{
    public $currentLatitude;
    public $currentLongitude;
    public $speed; // in meters per second

    public function __construct($currentLatitude, $currentLongitude, $speed) {
        $this->currentLatitude = $currentLatitude;
        $this->currentLongitude = $currentLongitude;
        $this->speed = $speed;
    }

    public function updatePosition($timeStep) {
        // Calculate the distance to move in each time step based on the speed
        $distanceToMove = $this->speed * $timeStep;

        // Convert the distance to degrees of latitude and longitude
        $degreesPerMeterLatitude = 1 / 111111; // Approximate conversion factor for latitude
        $degreesPerMeterLongitude = cos(deg2rad($this->currentLatitude)) / 111111; // Approximate conversion factor for longitude

        // Generate a random bearing (angle) in radians
        $bearing = deg2rad(mt_rand(0, 359));

        // Calculate the change in latitude and longitude coordinates based on the bearing and distance
        $deltaLatitude = $distanceToMove * $degreesPerMeterLatitude * sin($bearing);
        $deltaLongitude = $distanceToMove * $degreesPerMeterLongitude * cos($bearing);

        // Update the current position
        $this->currentLatitude += $deltaLatitude;
        $this->currentLongitude += $deltaLongitude;
    }
}

$entities = [];
$simulationTime = 60; // Total simulation time in seconds
$timeStep = 1; // Time step in seconds

// Create entities
for ($i = 0; $i < 1; $i++) {
    $entity = new Entity(26.712979, -80.049997, 10); // Provide initial latitude, longitude (e.g., Boston) and speed 10 m/s
    $entities[] = $entity;
}

function display_map($coordinates, $time) {
    echo "<div class='img-block'>";
    echo "<img src='https://maps.googleapis.com/maps/api/staticmap?center=26.713259,-80.052244&size=760x400&maptype=roadmap&scale=2&zoom=1\
&markers=size:tiny|color:red{$coordinates}|&key=AIzaSyCgWmMXzXgQDF3qai4VUz5Kxn07kBY9hsM' />";
    echo "<h2>Time: $time seconds</h2>";
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
            images.hide();
            images.eq(index).show();
            console.log(index);
            index++;
          }, 1000);

        });
      })(jQuery);
    </script>
    <style>
        .js-animation {
            display: none;
        }

        .img-block {
            position: absolute;
        }
    </style>
</head>
<body>
<div class="js-animation">
    <?php

    // Run the simulation
    for ($t = 0; $t < $simulationTime; $t += $timeStep) {
        $coordinates = "";
        // Update the position of each entity
        foreach ($entities as $entity) {
            $entity->updatePosition($timeStep);
            $coordinates .= "|" . $entity->currentLatitude . "," . $entity->currentLongitude;
//            echo "Position: ($entity->currentLatitude, $entity->currentLongitude)\n" . "<br />";
        }

        display_map($coordinates, $t);
//        echo "<h2>Time: $t seconds</h2>";
    }

    ?>
</div>
</body>
</html>


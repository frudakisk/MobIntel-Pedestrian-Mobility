<?php
require 'vendor/autoload.php';

use Tuupola\Trilateration\Intersection;
use Tuupola\Trilateration\Sphere;
use Phpml\Regression\LeastSquares;


$servername = "localhost";
$username = "root";
$password = "root";
$dbname = "trilateration";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

/**
 * trilaterates points and displays them on a map at different points in time,
 * selects distance from rssi using a linear regression model and values from MobIntel paper.
 * @param $rssi
 * @return string|void
 */
function trilaterate($rssi = 0) {
    $samples = [[-24], [-30], [-25], [-33], [-35], [-39], [-45], [-39], [-40], [-42], [-41], [-43], [-46], [-44],
        [-47], [-49], [-43], [-48], [-49], [-50], [-49], [-50], [-49], [-55]];
    $targets = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25];
    $regression = new LeastSquares();
    $regression->train($samples, $targets);
    $distance[] = $regression->predict([$rssi[0]]);
    $distance[] = $regression->predict([$rssi[1]]);
    $distance[] = $regression->predict([$rssi[2]]);

    $distance[] = 25;
    $distance[] = 7;
    $distance[] = 10;


    $sphere1 = new Sphere(26.713259, -80.052244, $distance[0]);
    $sphere2 = new Sphere(26.713262, -80.052443, $distance[1]);
    $sphere3 = new Sphere(26.713374, -80.052445, $distance[2]);

    $trilateration = new Intersection($sphere1, $sphere2, $sphere3);
    try {
        $point = $trilateration->position();
        $coordinate = "|" . $point->latitude() . "," . $point->longitude();
        return $coordinate;
    } catch (Exception $e) {
//        echo 'Caught exception: ', $e->getMessage(), "\n";
    }
}

function display_map($coordinates, $date = 'Y-m-d H:i:s') {
    echo "<div class='img-block'>";
    echo "<img src='https://maps.googleapis.com/maps/api/staticmap?center=26.713259,-80.052244&size=760x400&maptype=roadmap&scale=2&zoom=1\
&markers=size:tiny|color:red{$coordinates}|&markers=size:tiny|color:blue|26.713259,-80.052244|26.713262,-80.052443|26.713374,-80.052445|&key=AIzaSyCgWmMXzXgQDF3qai4VUz5Kxn07kBY9hsM' />";
    echo "<br />" . $date->format('Y-m-d H:i:s');
    echo "</div>";
} ?>

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

    $sql = "SELECT * FROM parquet ORDER BY probingtime ASC LIMIT 4000";
    $result = $conn->query($sql);
    $locations = [];

    if ($result->num_rows > 0) {
        // output data of each row
        $current_hour = null;
        $coordinates = "";
        do {
            $row = $result->fetch_assoc();
            $date = new DateTime($row['probingtime'], new DateTimeZone('America/New_York'));
            $hour = $date->format('H');
            if (!$row) {
                display_map($coordinates, $date);
                break;
            }
            if ($current_hour == null) {
                $current_hour = $hour;
                display_map($coordinates, $date);
                continue;
//                echo $current_hour . "<br />";
            }

            if ($hour > $current_hour) {
                display_map($coordinates, $date);
                $current_hour = $hour;
//                echo $current_hour . "<br />";
                $coordinates = [];
                continue;
            }

            $rssi = array($row['rssi_x'], $row['rssi_y'], $row['rssi']);
            $coordinate = trilaterate($rssi);

            if ($coordinate != null) {
                $coordinates .= $coordinate;
            }

        } while ($row = $result->fetch_assoc());
        // var_dump($coordinates);
    } else {
        echo "0 results";
    }
    $coordinate = trilaterate();
    display_map($coordinate);
    ?>
</div>
</body>
</html>

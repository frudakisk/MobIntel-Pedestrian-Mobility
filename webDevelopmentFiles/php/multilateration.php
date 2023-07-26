<?php
/**
 * This file was an attempt at multilateraion but the results were way worse than trilateration, i couldnt get this script to work properly.
 */


function distanceBetweenCoordinates($lat1, $lon1, $lat2, $lon2) {
    $earthRadius = 6371; // Earth's radius in kilometers

    $lat1Rad = deg2rad($lat1);
    $lon1Rad = deg2rad($lon1);
    $lat2Rad = deg2rad($lat2);
    $lon2Rad = deg2rad($lon2);

    $deltaLat = $lat2Rad - $lat1Rad;
    $deltaLon = $lon2Rad - $lon1Rad;

    $a = sin($deltaLat / 2) * sin($deltaLat / 2) +
        cos($lat1Rad) * cos($lat2Rad) *
        sin($deltaLon / 2) * sin($deltaLon / 2);

    $c = 2 * atan2(sqrt($a), sqrt(1 - $a));

    $distance = $earthRadius * $c;

    return $distance;
}

function convertToCartesian($latitude, $longitude) {
    $earthRadius = 6371; // Earth's radius in kilometers

    $x = $earthRadius * cos(deg2rad($latitude)) * cos(deg2rad($longitude));
    $y = $earthRadius * cos(deg2rad($latitude)) * sin(deg2rad($longitude));

    return array($x, $y);
}

function convertToGeographical($x, $y) {
    $earthRadius = 6371; // Earth's radius in kilometers

    $latitude = rad2deg(asin($y / $earthRadius));
    $longitude = rad2deg(atan2($x, $earthRadius * cos(asin($y / $earthRadius))));

    return array($latitude, $longitude);
}

function multilateration($anchors, $distances) {
    $numAnchors = count($anchors);

    if ($numAnchors < 3 || count($distances) !== $numAnchors) {
        return null; // Insufficient data or mismatched data
    }

    // Convert anchor coordinates to Cartesian system
    $cartesianAnchors = array();
    for ($i = 0; $i < $numAnchors; $i++) {
        $cartesianAnchors[] = convertToCartesian($anchors[$i][0], $anchors[$i][1]);
    }

    // Calculate weighted average of anchor coordinates based on distances
    $x = 0;
    $y = 0;
    $totalWeight = 0;

    for ($i = 0; $i < $numAnchors; $i++) {
        $weight = 1 / $distances[$i];
        $totalWeight += $weight;

        $x += $cartesianAnchors[$i][0] * $weight;
        $y += $cartesianAnchors[$i][1] * $weight;
    }

    // Divide by total weight to obtain final Cartesian coordinates
    $x /= $totalWeight;
    $y /= $totalWeight;

    // Convert Cartesian coordinates back to geographical system
    $geographicalCoordinates = convertToGeographical($x, $y);

    return $geographicalCoordinates;
}

function display_map($coordinates) {
    echo "<div class='img-block'>";
    echo "<img src='https://maps.googleapis.com/maps/api/staticmap?center=26.713259,-80.052244&size=760x400&maptype=roadmap&scale=2&zoom=1\
&markers=size:tiny|color:red{$coordinates}|&markers=size:tiny|color:blue|26.713259,-80.052244|26.713262,-80.052443|26.713374,-80.052445|&key=AIzaSyCgWmMXzXgQDF3qai4VUz5Kxn07kBY9hsM' />";
    // echo "<br />" . $date->format('Y-m-d H:i:s');
    echo "</div>";
} ?>

<!DOCTYPE html>
<html>
<head>
    <title></title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>
   <!-- <script>
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
    </style>-->
</head>
<body>
<div class="js-animation">
    <?php
    // Example usage
    $anchors = array(
        array(26.7133589, -80.0548058),   // Anchor 1 coordinates (latitude, longitude)
        array(26.7134373, -80.0548008),  // Anchor 2 coordinates (latitude, longitude)
        array(26.7133409, -80.054607)   // Anchor 3 coordinates (latitude, longitude)
    );

    $distances = array(300,400, 500); // Distances from the object to each anchor in kilometers

    $result = multilateration($anchors, $distances);
    $coordinates = "";
    if ($result !== null) {
        $latitude = $result[0];
        $longitude = $result[1];
        $coordinates .= "|" . $latitude . "," . $longitude;
        echo "The object is located at ($latitude, $longitude).";
    } else {
        echo "Insufficient or mismatched data provided.";
    }

   display_map($coordinates);
    ?>
</div>
</body>
</html>

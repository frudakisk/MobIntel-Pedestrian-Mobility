<?php

?>

<!DOCTYPE html>
<html>
<head>
    <title></title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>
</head>
<body>
<div>
    <?php
    function calculateDestinationCoordinate($latA, $lonA, $distance, $bearing) {
        $radius = 6371;  // Earth's radius in kilometers

        $latA = deg2rad($latA);
        $lonA = deg2rad($lonA);
        $bearing = deg2rad($bearing);

        $latB = asin(sin($latA) * cos($distance / $radius) + cos($latA) * sin($distance / $radius) * cos($bearing));
        $lonB = $lonA + atan2(sin($bearing) * sin($distance / $radius) * cos($latA), cos($distance / $radius) - sin($latA) * sin($latB));

        $latB = rad2deg($latB);
        $lonB = rad2deg($lonB);

        return array($latB, $lonB);
    }

    // Example usage
    $latitudeA = 26.713406;  // Latitude of starting point
    $longitudeA = -80.057136;  // Longitude of starting point
    $distance = 0.1;  // Distance in kilometers
    $bearing = 45;  // Bearing in degrees

    list($latitudeB, $longitudeB) = calculateDestinationCoordinate($latitudeA, $longitudeA, $distance, $bearing);
    echo "The new coordinate is: " . $latitudeB . " (latitude), " . $longitudeB . " (longitude)." . "<br />";

    echo "<img src='https://maps.googleapis.com/maps/api/staticmap?size=760x400
&markers=color:red|label:A|{$latitudeA},{$longitudeA}&markers=color:red|label:B|{$latitudeB},{$longitudeB}&key=AIzaSyCgWmMXzXgQDF3qai4VUz5Kxn07kBY9hsM'>";
    ?>
</div>
</body>
</html>


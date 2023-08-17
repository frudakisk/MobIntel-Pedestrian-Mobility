class Cell{
  /*This class will focus on the cells within the grid.
  Each cell will contain its own information that is callable */
  constructor(row, col, location, corners, center, sensor_distances, calculated_RSSI, avg_RSSI, score, hasSensor, localizationGuesses) {
    this.row = row;
    this.col = col;
    this.location = location;
    this.corners = corners;
    this.center = center;
    this.sensor_distances = sensor_distances;
    this.calculated_RSSI = calculated_RSSI;
    this.avg_RSSI = avg_RSSI;
    this.score = score;
    this.hasSensor = hasSensor;
    this.localizationGuesses = localizationGuesses;
  }

  handleClick() {
    /*This method prints out the information of the cell in a 
    pretty way.
    We can print out any of the Cell attributes, but to keep it simple
    for now, we just print the location*/
    console.log(`Cell clicked: (${this.row}, ${this.col})`);
    console.log(`Calculated RSSI ${this.calculated_RSSI}`);
    console.log(`Corners ${this.corners}`)
    let score = normalize(this.score);
    console.log(`Cell Score: ${this.score}`);
    let HTML = `Calculated RSSI: ${this.calculated_RSSI} <br />
                       Average RSSI: ${this.avg_RSSI} <br />
                       Sensor Distances: ${this.sensor_distances}<br />
                       Cell clicked: (${this.row}, ${this.col}) <br />
                       Score: ${this.score} <br />
                       hasSensor : ${this.hasSensor}`;
    return HTML;
  }
};


// Grid creation
const grid = document.getElementById('grid');
var r = document.querySelector(':root'); //access to css variables


function fetchData() {
  /*This function reads in a json form of the grid data that was
  prepared by phillip susman. This function also processes the data
  to be injected into each cell */
  
  //fetch('./grid_json.json')
  fetch('./170x25LargeGrid_json.json')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(jsonData => {
    // Process the JSON data
    //Will have to MANUALLY change columns and rows templates to whatever dimensions we decide for the grid
    captureDimensions(jsonData);
    processData(jsonData);
    resetCells();
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

function processData(data){
  let datalength = Object.keys(data).length;
  for (i = datalength - 1; i >= 0; i--) {
    // console.log(data[i])
    let infoLocation = data[i].location.slice(1, -1); //get rid of ()
    infoLocation = infoLocation.split(","); //turn to array [row,col]
    var rowNum = infoLocation[0];
    var colNum = infoLocation[1];
    var location = data[i].location;
    let corners = data[i].corners;
    let center = data[i].center;
    let sensorDistances = data[i].sensor_distances;
    let calculatedRssi = data[i].calculated_RSSI;
    let actualRssi = data[i].avg_RSSI;
    let score = data[i].score;
    let hasSensor = data[i].hasSensor;
    let localizationGuesses = data[i].localizationGuesses;
    createGridCell(rowNum, colNum, location, corners, center, sensorDistances,
        calculatedRssi, actualRssi, score, hasSensor, localizationGuesses);
  }
}

var rowNum = 0;
var colNum = 0;
function captureDimensions(jsonData) {
  /*
  jsonData: the json file in question
  This function captures the correct number of rows and columns
  that the data needs to be represented in. This is done by looking at
  the last entry of the json file and utilizing that location value.
  The location value is split into row value and column value. Each
  is incremented by one and then transfered over to the css file
  to tell us how many rows and columns we need to present
  */
  var jsonLastIndex = jsonData.length - 1;
  var lastEntry = jsonData[jsonLastIndex];
  var lastLocation = lastEntry['location']
  let infoLocation = lastLocation.slice(1, -1); //get rid of ()
  infoLocation = infoLocation.split(","); //turn to array [row,col]
  rowNum = Number(infoLocation[0]) + 1;
  colNum = Number(infoLocation[1]) + 1;
  r.style.setProperty('--rows', rowNum);
  r.style.setProperty('--columns', colNum);
}


function createGridCell(row, column, location, corners, center, sensor_distances, calculated_RSSI, avg_RSSI, score, hasSensor, localizationGuesses) {
  /*Creates an instance of Cell class and also
  creates a cell element that will be apart of the grid*/
  const cell = new Cell(row, column, location, corners, center, sensor_distances, calculated_RSSI, avg_RSSI, score, hasSensor, localizationGuesses);
  const cellElement = document.createElement('div');
  cellElement.className = 'cell';
  cellElement.textContent = 'Cell';
  if (cell.hasSensor != "[]") {
    //Give cells that have a sensor in it a thin black border
    cellElement.style.border = "thin solid #000000";
  }
  if (cell.avg_RSSI.indexOf("nan")) {
    console.log("NAN DETECTED IN AVG RSSI");
    console.log("SHOWING JSON SCORE IN CREATE GRID CELL")

    cell.avg_RSSI = cell.avg_RSSI.replaceAll("nan", "-9999");


  }

  if (cell.score.indexOf("nan")) {
    console.log("NAN DETECTED IN SCORE");

    cell.score = cell.score.replaceAll("nan", "-9999");
  }
  cellElement.addEventListener('click', () => showPopup(cell, cellElement));
  cellElement.cellinfo = cell;
  grid.appendChild(cellElement);
}

// Show popup with "cell location" message
function showPopup(cell, cellElement) {
  resetCells();
  const cells = document.getElementsByClassName('cell');
  const popup = document.getElementById('popup');
  const popupText = document.getElementById('popupText');
  cellElement.style.backgroundColor = 'purple';
  popupText.innerHTML = cell.handleClick();
  popup.style.display = 'block';

  let guesses_array = []; //will hold keys - tile locations
  let guesses_scores_array = [] //will hold values - localization guesses
  let localizationGuesses = cellElement.cellinfo.localizationGuesses;
  if (localizationGuesses.length > 2) {
    let guesses_object = stringToObject(localizationGuesses);
    let i = 0;
    //guesses_object is a dictionary object
    //guesses object has the localization score as the value, and tile spot as key
    console.log("guesses Object: ", guesses_object)
    for (const key in guesses_object) {
      let cell_number = getCell(key);
      guesses_array.push(cell_number);
      guesses_scores_array.push(guesses_object[key]);
    }
  }

  let stored_score = 0;
  for (let i = 0; i < cells.length; i++) {
    //going through each created cell
    for (let k = 0; k < guesses_array.length; k++) {
      //comparing each tile coord to the current iterated cell tile coord
      if (cells[i].cellinfo.row == guesses_array[k][0] && cells[i].cellinfo.col == guesses_array[k][1]) {
        current_score = guesses_scores_array[k];
        if(stored_score > current_score) {
          stored_score = current_score;
          //store the postion of the cell that has that score closest to 0
          highestScoreCell = cells[i];
        }

        //turning all localizations green
        cells[i].style.backgroundColor = `green`;
      }
    }
  }
  //turn highest score brown
  highestScoreCell.style.backgroundColor = `brown`;
}
 
// Resets cells to default state (background).
function resetCells() {
  let min_score = 100;
  let max_score = 0;
  const cells = document.getElementsByClassName('cell');
  let sensor_id = document.getElementById("sensor-select").value;
  console.log(sensor_id);

  // Loop through the selected elements set initial values and find max and min values
  for (let i = 0; i < cells.length; i++) {
    cells[i].style.backgroundColor = `rgba(255, 140, 0, 1)`;
    let score_JSON = cells[i].cellinfo.score;
    console.log("TYPE IN RESETCELLS")
    
    score_JSON = score_JSON.replace(/'/g, '"');
    let score = JSON.parse(score_JSON); //gotta do this to get actual data object and not string
    console.log(typeof(score))
    console.log(score)
    score = score[sensor_id];
    cells[i].cellinfo.sensor_score = score;
    if (score == -9999) {
      continue;
    }

    // need these scores in order to normalize the values for the background color opacity.
    if (score >= max_score)
      max_score = score;
    if (score <= min_score)
      min_score = score;
  }

  for (let i = 0; i < cells.length; i++) {
    let score = normalize(cells[i].cellinfo.sensor_score, min_score, max_score);
    cells[i].style.backgroundColor = `rgba(255,140,0, ${score})`;
  }
}

// utility function returns a value between 0 and 1
function normalize(val, min_score, max_score) {
  if (val == -9999) {
    return 0;
  }
  return (val - min_score) / (max_score - min_score) * (1 - 0.3) + 0.3;
}

// utility function to turn a string value into an object.
function stringToObject(input_string) {
// Step 1: Remove curly braces { and }
  const keyValuePairs = input_string.slice(1, -1);

// Step 2: Split the string by commas to get individual key-value pairs
  const pairsArray = keyValuePairs.split(/,\s*(?=\()/);

// Step 3: Create the JavaScript object
  const resultObject = {};

  pairsArray.forEach(pair => {
    const [property, value] = pair.split(': ');
    resultObject[property] = parseFloat(value);
  });

  return resultObject;
}

// parse coordinates value as string and return array
function getCell(input_string) {
  const regex = /\((-?\d+),\s*(-?\d+)\)/;
  const match = input_string.match(regex);

  if (match) {
    const numbersArray = [parseInt(match[1]), parseInt(match[2])];
    return numbersArray;
  }

  return false
}

// Hide popup when clicked outside of it
window.addEventListener('click', (event) => {
  const popup = document.getElementById('popup');
  if (event.target.tagName == 'HTML'){
    resetCells();
    popup.style.display = 'none';
  }
});

fetchData();

document.getElementById('sensor-select').addEventListener('change', function(e) {
  resetCells();
  return false;
});



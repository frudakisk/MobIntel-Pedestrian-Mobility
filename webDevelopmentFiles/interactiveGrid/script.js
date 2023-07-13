class Cell{
  /*This class will focus on the cells within the grid.
  Each cell will contain its own information that is callable */
  constructor(row, col, location, corners, center, sensor_distances, calculated_RSSI, avg_RSSI, score, hasSensor) {
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


function fetchData() {
  /*This function reads in a json form of the grid data that was
  prepared by phillip susman. This function also processes the data
  to be injected into each cell */
  fetch('./sampleGrid_json.json')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(jsonData => {
    // Process the JSON data
    //Will have to MANUALLY change columns and rows templates to whatever dimensions we decide for the grid
    let gridLength = 25;
    let gridWidth = 5;
    processData(jsonData);
    resetCells();
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

function processData(data){
  let datalength = Object.keys(data).length;
  for (i=datalength-1; i >= 0; i--){
    console.log(data[i])
    let infoLocation = data[i].location.slice(1,-1); //get rid of ()
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
    createGridCell(rowNum, colNum, location, corners, center, sensorDistances,
      calculatedRssi, actualRssi, score, hasSensor);
  }
}


function createGridCell(row, column, location, corners, center, sensor_distances, calculated_RSSI, avg_RSSI, score, hasSensor){
  /*Creates an instance of Cell class and also
  creates a cell element that will be apart of the grid*/
  const cell = new Cell(row, column, location, corners, center, sensor_distances, calculated_RSSI, avg_RSSI, score, hasSensor);
  const cellElement = document.createElement('div');
  cellElement.className = 'cell';
  cellElement.textContent = 'Cell';
  cellElement.addEventListener('click', () => showPopup(cell, cellElement));
  cellElement.cellinfo = cell;
  grid.appendChild(cellElement);
}

// Show popup with "cell location" message
function showPopup(cell, cellElement) {
  resetCells();
  const popup = document.getElementById('popup');
  const popupText = document.getElementById('popupText');
  cellElement.style.backgroundColor = 'purple';
  popupText.innerHTML = cell.handleClick();
  popup.style.display = 'block';
}

// Resets cells to default state (background).
function resetCells() {
  let min_score = 100;
  let max_score = 0;
  const cells = document.getElementsByClassName('cell');
  let sensor_id = document.getElementById("sensor-select").value;
  console.log(sensor_id);

  // Loop through the selected elements
  for (let i = 0; i < cells.length; i++) {
    cells[i].style.backgroundColor = `rgba(255,140,0,1)`;
    let score_JSON = cells[i].cellinfo.score;
    score_JSON = score_JSON.replace(/'/g, '"');
    let score = JSON.parse(score_JSON);
    score = score[sensor_id];
    cells[i].cellinfo.sensor_score = score;
    if (score == -9999) {
      continue;
    }
    if (score >= max_score) {
      max_score = score;
    }
    if (score <= min_score) {
      min_score = score;
    }
  }

  console.log(max_score);
  console.log(min_score);

  for (let i = 0; i < cells.length; i++) {
    let score = normalize(cells[i].cellinfo.sensor_score, min_score, max_score);
    /*console.log(cells[i].cellinfo.sensor_score);
    console.log(score);*/
    cells[i].style.backgroundColor = `rgba(255,140,0, ${score})`;
  }
}

function normalize(val, min_score, max_score) {
  if (val == -9999) {
    return 0;
  }
  return (val - min_score) / (max_score - min_score);
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



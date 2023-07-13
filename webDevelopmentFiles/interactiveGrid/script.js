class Cell{
  /*This class will focus on the cells within the grid.
  Each cell will contain its own information that is callable */
  constructor(row, col, location, corners, center, sensor_distances, calculated_RSSI, actual_RSSI, score) {
    this.row = row;
    this.col = col;
    this.location = location;
    this.corners = corners;
    this.center = center;
    this.sensor_distances = sensor_distances;
    this.calculated_RSSI = calculated_RSSI;
    this.actual_RSSI = actual_RSSI;
    //this.score = Math.floor(Math.random() * (1001 - 300) + 300);
    this.score = score
  }

  handleClick() {
    /*This method prints out the information of the cell in a 
    pretty way.
    We can print out any of the Cell attributes, but to keep it simple
    for now, we just print the location*/
    console.log(`Cell clicked: (${this.row}, ${this.col})`);
    console.log(`Calculated RSSI ${this.calculated_RSSI}`);
    let score = normalize(this.score);
    console.log(`Cell Score: ${score}`);
    let HTML = `Calculated RSSI: ${this.calculated_RSSI} <br />
                       Actual RSSI: ${this.actual_RSSI} <br />
                       Sensor Distances: ${this.sensor_distances}<br />
                       Cell clicked: (${this.row}, ${this.col}) <br />
                       Score: ${this.score}`;
    return HTML;
  }
};


// Grid creation
const grid = document.getElementById('grid');


function fetchData() {
  /*This function reads in a json form of the grid data that was
  prepared by phillip susman. This function also processes the data
  to be injected into each cell */
  fetch('./sampleGrid.json')
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
    processData(jsonData, gridLength, gridWidth);
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

function processData(data, gridLength, gridWidth){
  /*This function needs to process the data of each array
  and create the information for each cell.
  Each cell is corresponding to a tuple of (row#, col#) and we have to 
  flip the row# because if how html builds a grid and how python builds a
  grid. In python, origin is at the bottom left (0,0)
  In html, the origin is at the top left. */
  //for loop for row
  //for loop for column
  total = 0;
  let dataLength = Object.keys(data).length;
  console.log(dataLength); //printing length
  while(total < dataLength){
    for(i=0; i < gridWidth; i++){
      let rowNum = i + ((gridWidth-1)-(i*2)); //this is the translation //4 should be adjusted with gridWidth
      for(j=0; j < gridLength; j++){
        //for 170 cells, i need to change the row to the same number
        let info = data[total]

        let infoLocation = info.location.slice(1,-1); //get rid of ()
        infoLocation = infoLocation.split(","); //turn to array [row,col]
        console.log(infoLocation);
        infoLocation[0] = rowNum; //change row number
        infoLocation = "(" + infoLocation.toString() + ")"; //turn back to string
        data[total].location = infoLocation; //put back in json data
        console.log(data[total]);
        createGridCell(rowNum, j, data[total].location,
          data[total].corners, data[total].center, data[total].sensor_distances,
          data[total].calculated_RSSI, data[total].actual_RSSI, data[total].score)
        total ++;
      }
    }
  }
}

function createGridCell(row, column, location, corners, center, sensor_distances, calculated_RSSI, actual_RSSI, score){
  /*Creates an instance of Cell class and also
  creates a cell element that will be apart of the grid*/
  const cell = new Cell(row, column, location, corners, center, sensor_distances, calculated_RSSI, actual_RSSI, score);
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
  const cells = document.getElementsByClassName('cell');
  // Loop through the selected elements
  for (let i = 0; i < cells.length; i++) {
    console.log(cells[i]);
    cells[i].style.backgroundColor = `rgba(255,140,0,1)`;
    let score = normalize(cells[i].cellinfo.score);
    cells[i].style.backgroundColor = `rgba(255,140,0, ${score})`;
    // cells[i].style.filter = `brightness(${score}%)`;
  }
}

function normalize(val, max = 1000, min = 0) {
  return (val - min) / (max - min);
}


// Hide popup when clicked outside of it
window.addEventListener('click', (event) => {
  const popup = document.getElementById('popup');
  if (event.target.tagName == 'HTML'){
    resetCells();
    popup.style.display = 'none';
  }
});

fetchData()



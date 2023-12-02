let extendedDriverData = {};
let loadingInterval;
let percentLoaded = 0;

// Function to dynamically load all driver data from the JSON file
async function loadAllDriverData() {
    if (Object.keys(extendedDriverData).length === 0) {
        const response = await fetch('/f1/data/driver_statistics.json');
        extendedDriverData = await response.json();
    }
    return extendedDriverData;
}

// Function to fetch statistics for a specific driver
async function getDriverStatistics(driverId) {
    const allDriverData = await loadAllDriverData();
    return allDriverData[driverId] || {
        championships: 0,
        wins: 0,
        podiums: 0,
        points: 0,
        fastestLaps: 0,
        poles: 0,
        gpEntered: 0,
        laps_led: 0,
        seasons: 0
    };
}

// Function to start the loading indicator
function startLoadingIndicator() {
    const listContainer = document.getElementById('driverList');
    percentLoaded = 0;
    listContainer.innerHTML = '<div id="loadingIndicator" style="text-align: center;">Loading... 0%</div>';

    // Update the loading indicator every 100ms
    loadingInterval = setInterval(() => {
        percentLoaded++;
        document.getElementById('loadingIndicator').innerText = `Loading... ${percentLoaded}%`;
        if (percentLoaded >= 100) clearInterval(loadingInterval); // Stop increment at 100%
    }, 100);
}

// Function to stop the loading indicator
function stopLoadingIndicator() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.remove(); // Remove only the loading indicator
    }
}

// Updated GOAT score calculation function
function calculateGoatScore(stats) {
    const championships = stats.championships || 0;
    const wins = stats.wins || 0;
    const podiums = stats.podiums || 0;
    const points = stats.points || 0;
    const fastestLaps = stats.fastestLaps || 0;
    const poles = stats.poles || 0;
    const gpParticipations = stats.gpEntered || 0;
    const lapsLed = stats.laps_led || 0; // Corrected to laps_led
    const seasons = stats.seasons || 0;

    return (
        championships * 10 +
        wins * 2 +
        podiums +
        points * 0.1 +
        fastestLaps +
        poles +
        gpParticipations * 0.5 +
        lapsLed * 0.01 + // Corrected to laps_led
        seasons
    );
}

// Function to display drivers in an HTML table
async function displayDrivers() {
    const allDriverData = await loadAllDriverData();
    const listContainer = document.getElementById('driverList');
    listContainer.innerHTML = '';

    const drivers = Object.entries(allDriverData).map(([driverId, stats]) => ({
        name: stats.forename + ' ' + stats.surname,
        stats,
        goatScore: calculateGoatScore(stats)
    }));

    // Filter out null entries and sort by GOAT score
    const validDrivers = drivers.filter(driver => driver !== null);
    validDrivers.sort((a, b) => b.goatScore - a.goatScore);

    // Creating and appending a table to display the drivers
    const table = document.createElement('table');
    table.innerHTML = `
        <tr>
            <th>Rank</th>
            <th>Name</th>
            <th>Championships</th>
            <th>Wins</th>
            <th>Podiums</th>
            <th>Points</th>
            <th>Fastest Laps</th>
            <th>Poles</th>
            <th>GP Participations</th>
            <th>Laps Led</th>
            <th>Seasons</th>
            <th>Total GOAT Score</th>
        </tr>
    `;
    listContainer.appendChild(table);

    // Populating the table with driver data
    validDrivers.forEach((driver, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td><b>${driver.name}</b></td>
            <td>${driver.stats.championships}</td>
            <td>${driver.stats.wins}</td>
            <td>${driver.stats.podiums}</td>
            <td>${driver.stats.points}</td>
            <td>${driver.stats.fastestLaps}</td>
            <td>${driver.stats.poles}</td>
            <td>${driver.stats.gpEntered}</td>
            <td>${driver.stats.laps_led}</td>
            <td>${driver.stats.seasons}</td>
            <td>${driver.goatScore.toFixed(2)}</td>
        `;
        table.appendChild(row);
    });
}

// Function to initialize the display
async function initDriverDisplay() {
    await displayDrivers();
}
function hideLoadingIndicator() {
    const listContainer = document.getElementById('driverList');
    listContainer.innerHTML = ''; // Clear the loading message
}
async function loadDriverDataOnClick() {
    startLoadingIndicator();
    await displayDrivers();
}
document.getElementById('loadData').addEventListener('click', loadDriverDataOnClick);
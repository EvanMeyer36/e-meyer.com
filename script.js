document.addEventListener("DOMContentLoaded", function () {
    const gameButtons = document.querySelectorAll(".game-buttons button");
    const videoElement = document.getElementById("backgroundVideo");
    const stationButtons = document.getElementById("stationSelect");
    const radioPlayer = document.getElementById("radioPlayer");
    const volumeControl = document.getElementById("volumeControl");
    const gameVideos = {
        gta3: '/vid/gta3.mp4',
        vicecity: '/vid/vc.mp4',
        sanandreas: '/vid/sa.mp4',
        gta4: '/vid/gta4.mp4', // Add GTA IV video
    };
    // Define radio stations for GTA 3 and GTA Vice City
    const radioStations = {
        gta3: {
            'Head Radio': '/audio/gta3/HEAD.mp3',
            'Double Clef FM': '/audio/gta3/CLASS.mp3',
            'K-JAH': '/audio/gta3/KJAH.mp3',
            'Rise FM': '/audio/gta3/RISE.mp3',
            'Lips 106': '/audio/gta3/LIPS.mp3',
            'Game Radio': '/audio/gta3/GAME.mp3',
            'MSX FM': '/audio/gta3/MSX.wav',
            'Flashback 95.6': '/audio/gta3/FLASH.mp3',
            'Chatterbox FM': '/audio/gta3/CHAT.mp3',
        },
        vicecity: {
            'Wildstyle': '/audio/vc/WILD.mp3',
            'Flash FM': '/audio/vc/FLASH.mp3',
            'K-Chat': '/audio/vc/KCHAT.mp3',
            'Fever 105': '/audio/vc/FEVER.mp3',
            'V-Rock': '/audio/vc/VROCK.mp3',
            'VCPR': '/audio/vc/VCPR.mp3',
            'Radio Espantoso': '/audio/vc/ESPANT.mp3',
            'Wave 103': '/audio/vc/WAVE.mp3',
            'Emotion 98.3': '/audio/vc/EMOTION.mp3',
        },
        sanandreas: {
            'Playback FM': '/audio/sa/Playback FM.mp3',
            'K-Rose': '/audio/sa/K-Rose.mp3',
            'K-DST': '/audio/sa/K-DST.mp3',
            'Bounce FM': '/audio/sa/Bounce FM.mp3',
            'SF-UR': '/audio/sa/SF-UR.mp3',
            'Radio Los Santos': '/audio/sa/RLS.mp3',
            'Radio X': '/audio/sa/Radio X.mp3',
            'CSR 103.9': '/audio/sanandreas/CSR.mp3',
            'K-JAH West': '/audio/sanandreas/KJAH.mp3',
            'Master Sounds 98.3': '/audio/sa/Master Sounds 98.3.mp3',
            'WCTR': '/audio/sa/WCTR.mp3',
        },
        gta4: {
            'Electro-Choc': 'Electro-Choc.mp3',
            'Fusion FM': 'Fusion FM',
            'IF99 - International Funk': 'IF99',
            'Integrity 2.0': '/audio/gta4/Integrity 2.0.mp3',
            'Jazz Nation Radio 108.5': 'MP3 / FLAC - Jazz Nation Radio 108.5',
            'K109 The Studio': 'MP3 / FLAC - K109 The Studio',
            'Liberty City Hardcore': 'MP3 / FLAC - Liberty City Hardcore',
            'Liberty Rock Radio': 'MP3 / FLAC - Liberty Rock Radio',
            'Massive B Soundsystem 96.9': 'MP3 / FLAC - Massive B Soundsystem 96.9',
            'Public Liberty Radio': 'MP3 / FLAC - Public Liberty Radio',
            'Radio Broker': 'MP3 / FLAC - Radio Broker',
            'RamJam FM': 'MP3 / FLAC - RamJam FM',
            'San Juan Sounds': 'MP3 / FLAC - San Juan Sounds',
            'Self-Actualization FM': 'MP3 / FLAC - Self-Actualization FM',
            'The Beat 102.7': 'MP3 / FLAC - The Beat 102.7',
            'The Classics 104.1': 'MP3 / FLAC - The Classics 104.1',
            'The Journey': 'MP3 / FLAC - The Journey',
            'The Vibe 98.8': 'MP3 / FLAC - The Vibe 98.8',
            'Tuff Gong Radio': 'MP3 / FLAC - Tuff Gong Radio',
            'Vice City FM': 'MP3 / FLAC - Vice City FM',
            'Vladivostok FM': 'MP3 / FLAC - Vladivostok FM',
            'WKTT Radio': 'MP3 / FLAC - WKTT Radio',
            // Add more stations if needed
        },
    
    };
    function updateVideoSource(selectedGame) {
        const videoSource = gameVideos[selectedGame];
        videoElement.src = videoSource;
        videoElement.load();
    }

    // Add click event listeners to game buttons
    gameButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const selectedGame = button.dataset.game;
            populateStationIcons(selectedGame);
            updateVideoSource(selectedGame); // Update the video source
        });
    });
    // Function to update the "Now Playing" section
function updateNowPlaying(selectedGame, selectedStation) {
    const nowPlayingElement = document.getElementById("currentGameStation");
    nowPlayingElement.textContent = `${selectedGame} - ${selectedStation}`;
}

// Add click event listener to station buttons
stationButtons.addEventListener("click", function (event) {
    const target = event.target;

    if (target.classList.contains("radio-button")) {
        const selectedGame = target.dataset.game;
        const selectedStation = target.dataset.station;

        // Store the current playback position for the current station
        playbackPositions[selectedStation] = radioPlayer.currentTime;

        // Play the selected radio station
        playRadioStation(selectedGame, selectedStation);

        // Update the "Now Playing" section
        updateNowPlaying(selectedGame, selectedStation);
    }
});
    const playbackPositions = {};
    function populateStationIcons(selectedGame) {
        const stations = radioStations[selectedGame];
        const stationSelect = document.getElementById("stationSelect");
        stationSelect.innerHTML = ""; // Clear existing icons
    
        for (const station in stations) {
            const button = document.createElement("button");
            button.className = "radio-button";
            button.style.backgroundImage = `url('station_icons/${station}.png')`; // Set station icon background
            button.dataset.game = selectedGame;
            button.dataset.station = station;
            button.style.width = "160px"; // Set width to 160 pixels
            button.style.height = "120px"; // Set height to 120 pixels
            stationSelect.appendChild(button);
        }
    }
    
    
    // Function to play the selected radio station
    function playRadioStation(selectedGame, selectedStation) {
        if (selectedGame && selectedStation) {
            const audioSource = radioStations[selectedGame][selectedStation];
    
            // Calculate the audio duration (in seconds)
            const audio = new Audio(audioSource);
            audio.addEventListener("loadedmetadata", function () {
                const maxDuration = audio.duration;
    
                // Generate a random starting point between 0 and the audio duration
                const randomStartPosition = Math.random() * maxDuration;
    
                // Set the audio source dynamically based on the selected game and station
                radioPlayer.src = `${audioSource}#t=${randomStartPosition}`;
    
                // Play the selected radio station
                radioPlayer.play();
            });
    
            audio.load(); // Load the audio to get its duration
        }
    }
    
    // Add click event listeners to game buttons
    gameButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const selectedGame = button.dataset.game;
            populateStationIcons(selectedGame);
        });
    });
    

    // Add click event listener to station buttons
    stationButtons.addEventListener("click", function (event) {
        const target = event.target;

        if (target.classList.contains("radio-button")) {
            const selectedGame = target.dataset.game;
            const selectedStation = target.dataset.station;

            // Stop the current audio before switching to a new station
            radioPlayer.pause();

            // Store the current playback position for the current station
            playbackPositions[selectedStation] = radioPlayer.currentTime;

            // Play the selected radio station
            playRadioStation(selectedGame, selectedStation);
        }
    });

    // Add event listener to control volume
    volumeControl.addEventListener("input", function () {
        radioPlayer.volume = volumeControl.value;
    });

    // Play the initial radio station when the page loads
    playRadioStation("gta3", "Head Radio");
    updateVideoSource("gta3"); // Set the default video
});
const playPauseButton = document.getElementById("playPauseButton");
playPauseButton.addEventListener("click", function () {
    if (radioPlayer.paused) {
        radioPlayer.play(); // If paused, play the audio
    } else {
        radioPlayer.pause(); // If playing, pause the audio
    }
});
function populateStationIcons(selectedGame) {
    const stations = radioStations[selectedGame];
    const stationSelect = document.getElementById("stationSelect");
    stationSelect.innerHTML = ""; // Clear existing icons

    for (const station in stations) {
        const button = document.createElement("button");
        button.className = "radio-button";
        button.style.backgroundImage = `url('station_icons/${station}.png')`; // Set station icon background
        button.dataset.game = selectedGame;
        button.dataset.station = station;
        stationSelect.appendChild(button);
    }
}


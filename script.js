document.addEventListener("DOMContentLoaded", function () {
    const gameButtons = document.querySelectorAll(".game-buttons button");
    const videoElement = document.getElementById("backgroundVideo");
    const stationSelect = document.getElementById("stationSelect");
    const radioPlayer = document.getElementById("radioPlayer");
    const volumeControl = document.getElementById("volumeControl");
    const nowPlayingElement = document.getElementById("currentGameStation");


    const gameVideos = {
        gta3: '/vid/gta3.mp4',
        vicecity: '/vid/vc.mp4',
        sanandreas: '/vid/sa.mp4',
        gta4: '/vid/gta4.mp4',
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
            'MSX FM': '/audio/gta3/MSX.mp3',
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
            'CSR 103.9': '/audio/sa/CSR.mp3',
            'K-JAH West': '/audio/sa/KJAH.mp3',
            'Master Sounds 98.3': '/audio/sa/Master Sounds 98.3.mp3',
            'WCTR': '/audio/sa/WCTR.mp3',
        },
        gta4: {
            'Electro-Choc': '/audio/gta4/Electro-Choc.mp3',
            'Integrity 2.0': '/audio/gta4/Integrity 2.0.mp3',
            'Jazz Nation Radio 108.5': '/audio/gta4/Jazz Nation Radio 108.5.mp3',
            'K109 The Studio': '/audio/gta4/K109 The Studio.mp3',
            'Liberty City Hardcore': '/audio/gta4/Liberty City Hardcore.mp3',
            'Liberty Rock Radio': '/audio/gta4/Liberty Rock Radio.mp3',
            'Massive B Soundsystem 96.9': '/audio/gta4/Massive B Soundsystem 96.9.mp3',
            'Public Liberty Radio': '/audio/gta4/Public Liberty Radio.p3',
            'Radio Broker': '/audio/gta4/Radio Broker.mp3',
            'RamJam FM': '/audio/gta4/RamJam FM.mp3',
            'San Juan Sounds': '/audio/gta4/San Juan Sounds.mp3',
            'Self-Actualization FM': '/audio/gta4/Self-Actualization FM.mp3',
            'The Beat 102.7': '/audio/gta4/The Beat 102.7.mp3',
            'The Classics 104.1': '/audio/gta4/The Classics 104.1.mp3',
            'The Journey': '/audio/gta4/The Journey.mp3',
            'The Vibe 98.8': '/audio/gta4/The Vibe 98.8.mp3',
            'Tuff Gong Radio': '/audio/gta4/Tuff Gong Radio.mp3',
            'Vice City FM': '/audio/gta4/Vice City FM.mp3',
            'WKTT Radio': '/audio/gta4/Commercials.mp3',
            // Add more stations if needed
        },
    
    };
    let currentGame = "vicecity"; // Default game
    let currentStation = "Flash FM"; // Default station

    function updateVideoSource(selectedGame) {
        const videoSource = gameVideos[selectedGame];
        videoElement.src = videoSource;
        videoElement.load();
    }

    function updateNowPlaying() {
        nowPlayingElement.textContent = `Now Playing: ${currentGame} - ${currentStation}`;
    }

    function playRadioStation() {
        const audioSource = radioStations[currentGame][currentStation];
        radioPlayer.src = audioSource;
    
        // Check if a saved position exists for the current station
        const savedPosition = localStorage.getItem(currentStation);
    
        if (savedPosition !== null) {
            radioPlayer.currentTime = parseFloat(savedPosition);
        } else {
            // If no saved position, start at a random point within the audio duration
            const audioDuration = radioPlayer.duration;
            const randomPosition = Math.random() * audioDuration;
            radioPlayer.currentTime = randomPosition;
        }
    
        // Update the volume before playing
        radioPlayer.volume = volumeControl.value; // Set the volume based on the control's value
    
        radioPlayer.play();
    }
    

    function savePlaybackPosition() {
        localStorage.setItem(currentStation, radioPlayer.currentTime.toString());
    }

    function populateStationIcons() {
        const stations = radioStations[currentGame];
        stationSelect.innerHTML = "";

        for (const station in stations) {
            const button = document.createElement("button");
            button.className = "radio-button";
            button.style.backgroundImage = `url('station_icons/${station}.png')`;
            button.dataset.station = station;
            stationSelect.appendChild(button);
        }
    }

    gameButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            currentGame = button.dataset.game;
            updateVideoSource(currentGame);
            populateStationIcons();
        });
    });


    // Modify the stationSelect event listener to play the selected station
    stationSelect.addEventListener("click", function (event) {
        const target = event.target;
    
        if (target.classList.contains("radio-button")) {
            currentStation = target.dataset.station;
            savePlaybackPosition(); // Save playback position before switching stations
            playRadioStation(); // Play the selected station immediately
            updateNowPlaying();
    
            // Update the station image when a radio station is clicked
            const stationImage = document.getElementById("stationImage");
            stationImage.src = `station_images/${currentStation}.png`; // Set the image source based on the station
        }
    });

    // Listen for timeupdate event to continuously save playback position
    radioPlayer.addEventListener("timeupdate", savePlaybackPosition);

    updateVideoSource(currentGame);
    populateStationIcons();
    playRadioStation();
    updateNowPlaying();

    

    volumeControl.addEventListener("input", function () {
        radioPlayer.volume = volumeControl.value;
    });
});

const channels = [
  '/GTA TV/vid/weazel.mp4',
  '/GTA TV/vid/CNT.mp4'
];

let currentChannelIndex = 0;

function changeChannel(index) {
  const tvScreen = document.getElementById('tv-screen');
  
  // Play static noise for 1 second
  tvScreen.src = '/GTA TV/vid/static.mp4';
  tvScreen.muted = true;

  // Set a timeout to change to the actual channel video after 1 second
  setTimeout(() => {
    tvScreen.src = channels[index];
    
    // Load the video to get the metadata for duration
    tvScreen.load();
    
    // When the metadata is loaded, play the video at a random start time
    tvScreen.onloadedmetadata = () => {
      const randomTime = Math.random() * tvScreen.duration;
      tvScreen.currentTime = randomTime;
      tvScreen.play();
      tvScreen.muted = false;
    };
  }, 1000); // Duration of static video
}

function previousChannel() {
  let newIndex = currentChannelIndex - 1;
  if (newIndex < 0) {
    newIndex = channels.length - 1; // Wrap around to the last channel
  }
  currentChannelIndex = newIndex;
  changeChannel(newIndex);
}

function nextChannel() {
  let newIndex = currentChannelIndex + 1;
  if (newIndex >= channels.length) {
    newIndex = 0; // Wrap around to the first channel
  }
  currentChannelIndex = newIndex;
  changeChannel(newIndex);
}

function toggleMute() {
  const tvScreen = document.getElementById('tv-screen');
  tvScreen.muted = !tvScreen.muted; // Toggle the muted state
  // Update the button text based on the muted state
  const muteButton = document.getElementById('mute-button');
  muteButton.textContent = tvScreen.muted ? 'Unmute' : 'Mute';
}

// You might also want to update the initialization to unmute the video initially.
window.onload = () => {
  changeChannel(0);
  toggleMute(); // Make sure the video is unmuted when the page loads
};
function changeChannelButton() {
  // Call the changeChannel function with the desired channel index
  // For example, change to the second channel (index 1)
  changeChannel(1);
}
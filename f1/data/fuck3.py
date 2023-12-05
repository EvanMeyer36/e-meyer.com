from pytube import YouTube
import os

def download_youtube_video(url, path):
    # Create a YouTube object
    yt = YouTube(url)

    # Get the highest resolution stream
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

    # Download the video to the specified path
    if stream:
        stream.download(output_path=path)
        print(f"Downloaded: {yt.title} to {path}")
    else:
        print("No suitable stream found")

# Replace with your YouTube video URL
video_url = input("Enter Youtube URL: ")

# Specify your desired download path here
download_path = input("Enter your download path: ")

# Create directory if it doesn't exist
if not os.path.exists(download_path):
    os.makedirs(download_path)

download_youtube_video(video_url, download_path)
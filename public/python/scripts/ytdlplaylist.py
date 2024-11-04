import os
import yt_dlp
from pathlib import Path
import subprocess

# Configuration
playlist_url = "" # url for youtube playlist
download_folder = Path("") # Place path where files should be put
download_folder.mkdir(exist_ok=True)

# yt-dlp options
ydl_opts = {
    'outtmpl': str(download_folder / '%(title)s.%(ext)s'),
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
    'noplaylist': False,
    'merge_output_format': 'mp4',
}

def download_video(playlist_url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

def split_video(video_path, part_duration=3600):
    """Splits the video into parts of specified duration (in seconds)"""
    video_name = video_path.stem
    output_template = str(video_path.parent / f"{video_name}_part%03d.mp4")

    # Using ffmpeg to split video
    command = [
        "ffmpeg", "-i", str(video_path),
        "-c", "copy", "-map", "0",
        "-segment_time", str(part_duration),
        "-f", "segment", output_template
    ]
    subprocess.run(command)

def main():
    download_video(playlist_url)

    # Check for long videos and split if necessary
    for video_file in download_folder.glob("*.mp4"):
        file_size = video_file.stat().st_size
        # Check if the file size is too large (e.g., > 2GB)
        if file_size > 2 * 1024 * 1024 * 1024:  # 2GB threshold
            print(f"Splitting {video_file.name} due to large size...")
            split_video(video_file)
            os.remove(video_file)  # Remove original large file

if __name__ == "__main__":
    main()

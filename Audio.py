import os
import subprocess

def download_youtube_audio(video_url, output_dir):
    # Get the path to ffmpeg in the same directory as the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_path = os.path.join(script_dir, 'ffmpeg', 'bin', 'ffmpeg.exe')
    
    # Command to download only the best audio in MP3 format at 320kbps
    command = [
        'yt-dlp',
        '-o', f'{output_dir}/%(title)s.%(ext)s',
        '--extract-audio',  # Extract audio only
        '--audio-format', 'mp3',  # Convert to MP3
        '--audio-quality', '0',  # Best quality (320kbps)
        '--ffmpeg-location', ffmpeg_path,  # Use local ffmpeg
        video_url
    ]

    try:
        # Environment variable for proper encoding
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        # Run yt-dlp and capture output
        result = subprocess.Popen(
            command,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in result.stdout:
            print(line, end='')

        result.wait()
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, command)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

# Get the path to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Create Downloads folder in the same directory as the script if it doesn't exist
downloads_dir = os.path.join(script_dir, 'Downloads')
os.makedirs(downloads_dir, exist_ok=True)

# Prompt user for the video URL
video_url = input("Input YouTube video URL: ").strip()

# Call the function with the user-provided URL and output directory
download_youtube_audio(video_url, downloads_dir)
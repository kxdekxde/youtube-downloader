import os
import subprocess
import re 

def download_youtube_video(video_url, resolution, output_dir):
    # Clean the resolution to ensure it only contains numbers and 'p'
    resolution_clean = re.sub(r'[^\dp]', '', resolution)  # Keep only digits and 'p'
    
    # Command to download video with the best available audio and video streams
    command = [
        'yt-dlp',
        '-o', f'{output_dir}/%(title)s_{resolution_clean}p.%(ext)s',
        '--format', f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]',
        '--merge-output-format', 'mp4',
        '--ffmpeg-location', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg', 'bin'),
        video_url
    ]

    try:
        # Environment variable for proper encoding
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        # Run yt-dlp and capture output with UTF-8 encoding
        result = subprocess.Popen(
            command,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,  # Also capture stderr
            text=True,  # Ensure text mode
            encoding='utf-8',  # Explicitly set UTF-8 encoding
            bufsize=1
        )

        # Print output from both stdout and stderr
        for line in result.stdout:
            print(line, end='')

        for line in result.stderr:
            print(line, end='')

        result.wait()
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, command)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

# Get the path to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
# Set the output directory to "Downloads" folder in the script's directory
output_dir = os.path.join(script_dir, 'Downloads')

# Create the Downloads directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Prompt user for the video URL
video_url = input("Input YouTube video URL: ").strip()

# Prompt user for the resolution
print("Available options: 2160, 1440, 1080, 720, 480, 360, 240, 144")
resolution = input("Input quality (e.g., 2160, 1440, 1080, 720, 480, 360, 240, 144): ").strip()

if not resolution.isdigit() and not re.match(r'\d+p\d+', resolution):  # Check if resolution is valid
    print("Invalid input. Please enter a valid resolution (e.g., 720, 480 or 720p60).")
else:
    # Call the function with the user-provided URL and resolution
    download_youtube_video(video_url, resolution, output_dir)
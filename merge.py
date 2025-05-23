import os
import subprocess
import argparse
import logging

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Merge subtitle files with videos using mkvmerge.")
parser.add_argument("--input-folder", "-i", type=str, default=os.path.dirname(os.path.abspath(__file__)), help="Folder containing video and subtitle files (default: script directory)")
parser.add_argument("--output-folder", "-o", type=str, default=os.path.dirname(os.path.abspath(__file__)), help="Folder to save merged output files (default: same as input)")
parser.add_argument("--charset", "-c", type=str, default="UTF-8", help="Character encoding of subtitle files (default: UTF-8)")
args = parser.parse_args()

input_folder = args.input_folder
output_folder = args.output_folder
charset = args.charset

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# Configure logging
log_path = os.path.join(output_folder, "merge_log.txt")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logging.info(f"Starting subtitle merge in: {input_folder}")

# Iterate over video files in the input folder
for file_name in os.listdir(input_folder):
    if file_name.lower().endswith((".mp4", ".mkv")):
        video_path = os.path.join(input_folder, file_name)

        # Construct subtitle file path based on video filename
        srt_name = os.path.splitext(file_name)[0] + ".srt"
        srt_path = os.path.join(input_folder, srt_name)

        # Proceed if the corresponding subtitle file exists
        if os.path.exists(srt_path):
            output_name = os.path.splitext(file_name)[0] + "-merged.mkv"
            output_path = os.path.join(output_folder, output_name)

            # Build the mkvmerge command
            mkvmerge_command = [
                "mkvmerge",
                "-o", output_path,
                video_path,
                "--language", "0:ro", srt_path,
                "--sub-charset", "0:" + charset
            ]

            # Execute the command to merge video and subtitles
            try:
                subprocess.run(mkvmerge_command, check=True)
                logging.info(f"Successfully merged: {file_name} with {srt_name} -> {output_name}")
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to merge {file_name} with {srt_name}. Error: {e}")
        else:
            logging.warning(f"No corresponding SRT file found for: {file_name}")

logging.info("Subtitle merge process completed.")

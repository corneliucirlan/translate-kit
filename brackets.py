import argparse
import re
import sys
import os
import logging

from common.parse import parse_srt

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def remove_bracketed_and_parenthesized_text_from_subtitle(subtitle):
    """Removes text within square brackets and parentheses from a Subtitle object's text."""
    subtitle.text = re.sub(r'\[.*?\]|\(.*?\)', '', subtitle.text).strip()
    return subtitle

def write_srt(subtitles, output_file_path):
    """Writes a list of Subtitle objects to an SRT file, skipping empty text and renumbering IDs."""
    try:
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            subtitle_counter = 1
            for subtitle in subtitles:
                if subtitle.text:  # Check if the text is not empty
                    subtitle.id_line = str(subtitle_counter)  # Update the ID
                    outfile.write(str(subtitle) + "\n\n")
                    subtitle_counter += 1
        print(f"Processed and saved: {os.path.basename(output_file_path)}")
    except Exception as e:
        print(f"An error occurred while writing to '{os.path.basename(output_file_path)}': {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove lines that are wrapped in brackets")
    parser.add_argument("--input", "-i", type=str, default=".", help="Input directory containing the SRT files")
    parser.add_argument("--output", "-o", type=str, default="output", help="Output directory for the processed SRT files")
    args = parser.parse_args()

    # Create the output folder if it doesn't exist
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        print(f"Created output folder: {args.output}")

    # Iterate through all files in the input folder
    for filename in os.listdir(args.input):
        if filename.endswith(".srt") and os.path.isfile(os.path.join(args.input, filename)):
            input_file_path = os.path.join(args.input, filename)
            output_file_path = os.path.join(args.output, filename)

            # Parse the SRT file into a list of Subtitle objects
            subtitles = parse_srt(input_file_path)

            # Process each subtitle object
            modified_subtitles = []
            for subtitle in subtitles:
                modified_subtitle = remove_bracketed_and_parenthesized_text_from_subtitle(subtitle)
                modified_subtitles.append(modified_subtitle)

            # Write the modified subtitle objects to the output file
            write_srt(modified_subtitles, output_file_path)

    print("\nFinished processing SRT files.")
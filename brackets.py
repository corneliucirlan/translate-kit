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
    if len(sys.argv) != 3:
        print("Usage: python script_name.py <input_folder_path> <output_folder_path>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")

    # Iterate through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".srt") and os.path.isfile(os.path.join(input_folder, filename)):
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename)

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
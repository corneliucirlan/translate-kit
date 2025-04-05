import re
import logging

from common.subtitle import Subtitle

def parse_srt(srt_file_path):
    """Parses an SRT file and returns a list of Subtitle objects."""
    subtitles = []
    try:
        with open(srt_file_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()
    except FileNotFoundError:
        logging.error(f"File not found: {srt_file_path}")
        return []
    except Exception as e:
        logging.error(f"Error reading file {srt_file_path}: {e}")
        return []

    # Use a more robust regex to handle different line endings and spacing
    subtitle_blocks = re.split(r'\n\s*\n', srt_content.strip())

    for block in subtitle_blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            id_line = lines[0].strip()
            timestamps = lines[1].strip()
            text = '\n'.join(lines[2:]).strip()
            # Basic validation for ID and timestamp format (optional but good)
            if id_line.isdigit() and '-->' in timestamps:
                subtitles.append(Subtitle(id_line, timestamps, text))
            else:
                logging.warning(f"Skipping invalid subtitle block fragment in {srt_file_path}: ID='{id_line}', Timestamp='{timestamps}'")
        elif block.strip(): # Avoid warnings for empty blocks resulting from split
            logging.warning(f"Skipping incomplete subtitle block in {srt_file_path}: {block}")
    return subtitles
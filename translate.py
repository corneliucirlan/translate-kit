import os
import re
import asyncio
import argparse
import logging
from openai import OpenAI, OpenAIError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize OpenAI client (ensure OPENAI_API_KEY environment variable is set)
try:
    client = OpenAI()
except OpenAIError as e:
    logging.error(f"Failed to initialize OpenAI client: {e}")
    # Consider exiting or handling this appropriately
    client = None # Prevent further errors if initialization failed

class Subtitle:
    def __init__(self, id_line, timestamps, text):
        # Store id_line as string to preserve original formatting if needed
        self.id_line = id_line
        self.timestamps = timestamps
        self.text = text

    def __str__(self):
        # Reconstruct the standard SRT block format
        return f"{self.id_line}\n{self.timestamps}\n{self.text}"

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

def chunk_subtitles_as_text(subtitles, chunk_size=50):
    """
    Chunks a list of Subtitle objects into single strings,
    each containing multiple subtitle blocks in SRT format.
    Reduced chunk size for better API response time and reliability.
    """
    chunks = []
    for i in range(0, len(subtitles), chunk_size):
        chunk = subtitles[i:i + chunk_size]
        # Join individual subtitle string representations with double newlines
        chunk_string = "\n\n".join(str(subtitle) for subtitle in chunk)
        chunks.append(chunk_string)
    return chunks

async def translate_chunk(chunk_text, original_language, target_language, model, retries=3, delay=5):
    """Translates a single chunk of SRT text using OpenAI API with retries."""
    if not client:
        logging.error("OpenAI client not initialized. Cannot translate.")
        return None # Or raise an exception

    prompt = f"""Translate ONLY the text portions of the following SRT subtitle blocks from {original_language} to {target_language}.
Maintain the EXACT original formatting, including the subtitle index numbers and timestamps.
Do NOT add any extra explanations, introductory text, or closing remarks.
Output ONLY the translated SRT blocks.

Input SRT Chunk:
```srt
{chunk_text}"""

    for attempt in range(retries):
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert SRT subtitle translator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2, # Lower temperature for more deterministic translation
                # max_tokens=... # Consider setting max_tokens based on chunk size
            )
            translated_text = response.choices[0].message.content.strip()

            # Basic validation: Check if the output looks like SRT
            if "-->" in translated_text and translated_text.strip().endswith("```"):
                 # Clean up potential markdown code block fences
                 translated_text = translated_text.replace("```srt", "").replace("```", "").strip()
                 return translated_text
            else:
                 logging.warning(f"Received potentially malformed translation for chunk. Attempt {attempt + 1}/{retries}. Content: {translated_text[:100]}...")
                 # Don't retry immediately if content is bad, maybe it's a prompt issue

        except OpenAIError as e:
            logging.warning(f"OpenAI API error on attempt {attempt + 1}/{retries}: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay * (attempt + 1)) # Exponential backoff
            else:
                logging.error(f"Failed to translate chunk after {retries} attempts.")
                return None # Failed to translate this chunk
        except Exception as e:
            logging.error(f"An unexpected error occurred during translation: {e}")
            return None # Non-API error

    return None # Return None if all retries fail

async def process_srt_file(input_srt_file, output_dir, source_language, target_language, model):
    """Parses, chunks, translates, and writes a single SRT file."""
    if not os.path.exists(input_srt_file):
        logging.error(f"Input file '{input_srt_file}' not found.")
        return

    logging.info(f"Processing SRT file: {input_srt_file}")
    subtitles = parse_srt(input_srt_file)
    if not subtitles:
        logging.warning(f"No valid subtitles found in {input_srt_file}. Skipping.")
        return

    # Chunk size reduced to 50 for potentially better results and faster individual API calls
    chunks = chunk_subtitles_as_text(subtitles, 50)
    logging.info(f"Subtitle count: {len(subtitles)}, Chunks: {len(chunks)}")

    output_file_name = os.path.splitext(os.path.basename(input_srt_file))[0] + "_out.srt"
    output_file_path = os.path.join(output_dir, output_file_name)

    translated_chunks = []
    tasks = [translate_chunk(chunk, source_language, target_language, model) for chunk in chunks]
    results = await asyncio.gather(*tasks) # Run translation tasks concurrently

    # Filter out None results (failed translations)
    successful_translations = [result for result in results if result is not None]

    if len(successful_translations) != len(chunks):
        logging.warning(f"File {input_srt_file}: Only {len(successful_translations)} out of {len(chunks)} chunks were successfully translated.")
        # Decide if partial translation is acceptable or should be an error

    if not successful_translations:
         logging.error(f"No chunks were successfully translated for {input_srt_file}. Output file will not be created.")
         return

    # Write the successfully translated chunks to the output file
    try:
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            # Join translated chunks with double newlines
            full_translation = "\n\n".join(successful_translations)
            outfile.write(full_translation)

            # Ensure the file ends with a newline if needed by players
            if not full_translation.endswith('\n'):
                 outfile.write('\n')
        logging.info(f"Successfully wrote translated subtitles to: {output_file_path}")
    except IOError as e:
        logging.error(f"Error writing output file {output_file_path}: {e}")


async def main(input_dir, output_dir, source_language, target_language, model):
    """Main function to find and process SRT files concurrently."""
    if not client:
        logging.error("OpenAI client failed to initialize. Exiting.")
        return

    if not os.path.isdir(input_dir):
        logging.error(f"Input directory '{input_dir}' not found or is not a directory.")
        return

    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logging.info(f"Created output directory: {output_dir}")
        except OSError as e:
            logging.error(f"Failed to create output directory '{output_dir}': {e}")
            return

    srt_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir)
                 if os.path.isfile(os.path.join(input_dir, f)) and f.lower().endswith(".srt")]

    if not srt_files:
        logging.info(f"No SRT files found in the input directory '{input_dir}'.")
        return

    logging.info(f"Found {len(srt_files)} SRT files to process.")

    # Create tasks for each file processing coroutine
    tasks = [process_srt_file(file_path, output_dir, source_language, target_language, model) for file_path in srt_files]

    # Run all file processing tasks concurrently
    await asyncio.gather(*tasks)

    logging.info("Processing complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate SRT subtitle files using OpenAI API.")
    parser.add_argument("--input", "-i", type=str, default=".", help="Input directory containing SRT files.")
    parser.add_argument("--output", "-o", type=str, default="output", help="Output directory for translated SRT files.")
    parser.add_argument("--source-language", "-sl", type=str, default="English", help="Original language of the SRT files")
    parser.add_argument("--target-language", "-tl", type=str, default="Romanian", help="Desired language of the translated SRT files")
    parser.add_argument("--model", "-m", type=str, default="gpt-4o-mini", help="OpenAI model to use for translation.")
    args = parser.parse_args()

    # Ensure the main function runs within the asyncio event loop
    asyncio.run(main(args.input, args.output, args.source_language, args.target_language, args.model))

import os
import re
import asyncio
import argparse
import logging
from openai import OpenAI, OpenAIError
from common.parse import parse_srt

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize OpenAI client
try:
    client = OpenAI()
except OpenAIError as e:
    logging.error(f"Failed to initialize OpenAI client: {e}")
    client = None

def chunk_subtitles_as_text(subtitles, chunk_size=20):
    chunks = []
    for i in range(0, len(subtitles), chunk_size):
        chunk = subtitles[i:i + chunk_size]
        chunk_string = "\n\n".join(str(subtitle) for subtitle in chunk)
        chunks.append(chunk_string)
    return chunks

async def translate_chunk(chunk_text, original_language, target_language, model, dry_run=False, retries=3, delay=5):
    if dry_run:
        logging.info("[Dry-run] Skipping actual translation.")
        return chunk_text

    if not client:
        logging.error("OpenAI client not initialized. Cannot translate.")
        return None

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
                temperature=0.2
            )
            translated_text = response.choices[0].message.content.strip()
            translated_text = re.sub(r"```srt", "", translated_text, flags=re.IGNORECASE).strip()
            translated_text = re.sub(r"```", "", translated_text).strip()

            if "-->" in translated_text:
                return translated_text
            else:
                logging.warning(f"Chunk format issue on attempt {attempt + 1}/{retries}: {translated_text[:100]}...")

        except OpenAIError as e:
            logging.warning(f"OpenAI API error on attempt {attempt + 1}/{retries}: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay * (attempt + 1))
            else:
                logging.error("Failed after retries.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return None

    return None

async def process_srt_file(input_srt_file, output_dir, source_language, target_language, model, dry_run=False):
    if not os.path.exists(input_srt_file):
        logging.error(f"Input file '{input_srt_file}' not found.")
        return

    logging.info(f"Processing SRT file: {input_srt_file}")
    subtitles = parse_srt(input_srt_file)
    if not subtitles:
        logging.warning(f"No valid subtitles found in {input_srt_file}.")
        return

    chunks = chunk_subtitles_as_text(subtitles, 20)
    logging.info(f"Subtitles: {len(subtitles)}, Chunks: {len(chunks)}")

    output_file_name = os.path.splitext(os.path.basename(input_srt_file))[0] + "_out.srt"
    output_file_path = os.path.join(output_dir, output_file_name)

    tasks = [translate_chunk(chunk, source_language, target_language, model, dry_run=dry_run) for chunk in chunks]
    results = await asyncio.gather(*tasks)
    successful_translations = [r for r in results if r is not None]

    if not dry_run and successful_translations:
        try:
            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                full_translation = "\n\n".join(successful_translations)
                outfile.write(full_translation)
                if not full_translation.endswith('\n'):
                    outfile.write('\n')
            logging.info(f"Wrote translated subtitles to: {output_file_path}")
        except IOError as e:
            logging.error(f"Error writing file {output_file_path}: {e}")
    elif dry_run:
        logging.info(f"[Dry-run] Skipped writing output for: {input_srt_file}")

async def main(input_dir, output_dir, source_language, target_language, model, dry_run=False):
    if not dry_run and not client:
        logging.error("OpenAI client failed to initialize.")
        return

    if not os.path.isdir(input_dir):
        logging.error(f"Input directory '{input_dir}' is invalid.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Created output directory: {output_dir}")

    srt_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir)
                 if os.path.isfile(os.path.join(input_dir, f)) and f.lower().endswith(".srt")]

    if not srt_files:
        logging.info(f"No SRT files found in: {input_dir}")
        return

    logging.info(f"Found {len(srt_files)} SRT files.")
    tasks = [process_srt_file(f, output_dir, source_language, target_language, model, dry_run=dry_run)
             for f in srt_files]
    await asyncio.gather(*tasks)
    logging.info("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate SRT subtitle files using OpenAI API.")
    parser.add_argument("--input", "-i", type=str, default=".", help="Input directory containing SRT files.")
    parser.add_argument("--output", "-o", type=str, default="output", help="Output directory for translated SRT files.")
    parser.add_argument("--source-language", "-sl", type=str, default="English", help="Original language.")
    parser.add_argument("--target-language", "-tl", type=str, default="Romanian", help="Target language.")
    parser.add_argument("--model", "-m", type=str, default="gpt-4o-mini", help="OpenAI model to use.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate translation without API calls or writing output.")
    args = parser.parse_args()

    asyncio.run(main(args.input, args.output, args.source_language, args.target_language, args.model, dry_run=args.dry_run))

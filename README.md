# SRT Subtitle Translator (using OpenAI API)

A Python script to automatically translate `.srt` subtitle files from one language to another using the OpenAI API, preserving timestamps and formatting.

## Overview

This script processes `.srt` files located in a specified input directory. It reads each file, chunks the subtitles into manageable blocks, sends them to the OpenAI API for translation, and then writes the translated subtitles (maintaining the original structure) to a specified output directory. It uses `asyncio` for concurrent processing of files and API calls, potentially speeding up the translation of multiple files or large files.

## Features

* Translates `.srt` subtitle text content.
* Preserves original subtitle index numbers and timestamps.
* Processes all `.srt` files within a specified directory.
* Chunks subtitles to handle potentially large files and improve API reliability.
* Uses the OpenAI API for translation (configurable model).
* Asynchronous processing using `asyncio` for potentially faster execution.
* Configurable source and target languages.
* Basic error handling and retry mechanism for API calls.
* Command-line interface for easy configuration.

## Requirements

* Python 3.7+ (due to `asyncio` usage and type hints)
* `openai` Python library
* An OpenAI API Key


## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/corneliucirlan/translate-kit.git
    cd translate-kit
    ```

2.  **Install dependencies:**
    It's recommended to use a virtual environment:
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate

    pip install openai
    ```

3.  **Set up OpenAI API Key:**
    The script requires your OpenAI API key to be set as an environment variable named `OPENAI_API_KEY`.
    * **macOS/Linux:**
        ```bash
        export OPENAI_API_KEY='your-api-key-here'
        ```
    * **Windows (Command Prompt):**
        ```bash
        set OPENAI_API_KEY=your-api-key-here
        ```
    * **Windows (PowerShell):**
        ```bash
        $env:OPENAI_API_KEY='your-api-key-here'
        ```
    Alternatively, you can modify the script to load the key from a `.env` file using a library like `python-dotenv`.


## Usage

Run the script from your terminal using `python translate.py`. Use the command-line arguments to configure its behavior.

  ```bash
  python translate.py [OPTIONS]
```


## Options

### `--input DIRECTORY` or `-i DIRECTORY`
Specifies the directory containing the source `.srt` subtitle files you want to translate.

- **Default:** `.` (The directory where you are currently running the script).
- **Example:**  
  ```bash
  python translate.py -i ./path/to/your/subtitles
  ```

### `--output DIRECTORY` or `-o DIRECTORY`
Specifies the directory where the translated .srt files will be saved. The script will attempt to create this directory if it doe not exist.

- **Default:** output (A folder named "output" will be created in the current directory).
- **Example:**
  ```bash
  python translate.py -o ./translated_subtitles
  ```

### `--source-language LANGUAGE` or `-sl LANGUAG`
Defines the original language of the subtitles in the input files (e.g., "English", "Spanish", "French"). This information is passed to the translation model.

- **Default:** `English`
- **Example:**
  ```bash
  python translate.py -sl German
  ```

### `--target-language LANGUAGE` or `-tl LANGUAGE`
Defines the language you want the subtitles translated into (e.g., "Romanian", "Japanese", "Italian").

- **Default:** `Romanian`
- **Example:**  
  ```bash
  python translate.py -tl "Brazilian Portuguese"

### `--model MODEL_NAME` or `-m MODEL_NAME`
Specifies the OpenAI model to use for the translation task. Different models may offer varying translation quality, speed, and cost.

- **Default:** `gpt-4o-mini`
- **Example:**  
  ```bash
  python translate.py -m gpt-4
  python translate.py -m gpt-3.5-turbo
  ```
(Consult the OpenAI documentation for currently available and suitable chat completion models.)


## Examples

Translate English `.srt` files in `./subs_en` folder to Romanian in `./subs_ro` using the default model (`gpt-4o-mini`):
  ```bash
  python translate.py -i ./subs_en -o ./subs_ro -sl English -tl Romanian
  ```
Translate French `.srt` files in the current directory (`.`) to German in `./output_de` using the `gpt-4` model:
  ```bash
  python translate.py --input . --output ./output_de --source-language French --target-language German --model gpt-4
  ```
Use defaults (translate English `.srt` files in the current directory (`.`) to Romanian in `./output` using `gpt-4o-mini`):
  ```bash
  python translate.py
  ```

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
    git clone <your-repository-url>
    cd <repository-name>
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

Run the script from your terminal using `python translate_srt.py` (or whatever you name the main Python file). Use the command-line arguments to configure its behavior.

```bash
python translate_srt.py [OPTIONS]
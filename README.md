# MJD Python Scripts 🐍

A curated repository containing a diverse collection of Python scripts developed by John Dowe, spanning various functionalities from utility tools to more complex applications.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0.html)

## About This Repository

This repository, `python_scripts`, serves as a central hub for John Dowe's Python projects. It showcases a range of scripts and applications, demonstrating proficiency in different Python libraries and programming paradigms. The collection includes tools for browsing, video censorship, and a shopping calculator, among others.

## Key Features

*   **Adult Browser (`adult_browser`)**: A standalone desktop browser application built with PySide6, featuring a custom dark interface, site shortcuts, an address bar, navigation controls, and tabbed browsing. Websites are loaded as top-level Chromium WebEngine pages.
*   **AutoCensorVideo (`adult_video_censorship`)**: An advanced video censorship utility for Windows. It offers modular architecture, batch processing, a modern GUI (CustomTkinter), video preview, real-time configuration editing, and detailed processing statistics. It supports multiple overlay types (blur, pixelate, emoji, box, image) and integrates with MediaPipe for face detection and NudeNet/YOLO for private region detection.
*   **Dowe Shopping Calculator (`ShoppingCalculator`)**: A command-line application for managing shopping lists and calculating sales tax for Pueblo, Colorado. It utilizes the `rich` library for a user-friendly console interface and supports exporting receipts in TXT, CSV, and JSON formats.
*   **Utility Scripts**: Various other Python scripts and utilities are included, demonstrating a breadth of Python development capabilities.

## Tech Stack

*   **Languages**: Python, Markdown, Text, JSON
*   **Frameworks & Libraries**: PySide6, CustomTkinter, OpenCV, MediaPipe, Pillow, Ultralytics, NudeNet, tqdm, Pytest, imageio, imageio-ffmpeg, Rich, NumPy

## Installation

This repository contains multiple independent projects. Please refer to the specific project's README for detailed installation instructions.

### General Python Environment Setup

1.  **Ensure Python is installed**: Version 3.10+ (64-bit) is recommended for most projects.
2.  **Clone the repository**: 
    ```bash
    git clone https://github.com/mrjohndowe/python_scripts.git
    cd python_scripts
    ```

### Specific Project Installations:

*   **Adult Browser**:
    Navigate to the `adult_browser` directory and install dependencies:
    ```powershell
    py -m pip install -r requirements.txt
    ```

*   **AutoCensorVideo**:
    Navigate to the `adult_video_censorship` directory. It's recommended to create and activate a virtual environment:
    ```powershell
    py -3.14 -m venv .venv
    ..venvScriptsActivate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```
    **FFmpeg**: Ensure FFmpeg and FFprobe are installed and accessible in your system's PATH.
    **MediaPipe Face Detector**: Download the model as instructed in the `adult_video_censorship/README.md`.

*   **Shopping Calculator**:
    This project has minimal external dependencies beyond standard Python libraries and `rich` for enhanced console output. It can typically be run directly after cloning.

## Usage Examples

### Adult Browser

Run the `adult_video_sidebar.py` script from the `adult_browser` directory:

```powershell
py adult_video_sidebar.py
```

### AutoCensorVideo

**GUI Mode (Recommended):**
```powershell
python run_gui.py
```

**CLI Mode:**
```powershell
python run.py
```

This will prompt you to select a processing mode (single video, batch, preview, configuration).

### Shopping Calculator

Run the main script to start the interactive menu:

```bash
python ShoppingCalculator/main.py
```

## Project Structure

The repository contains several distinct projects:

*   **`adult_browser/`**: Contains the desktop browser application.
    *   `requirements.txt`: PySide6 dependencies.
    *   `adult_video_sidebar.py`: Main application script.
*   **`adult_video_censorship/`**: Houses the video censorship utility.
    *   `autocensor/`
        *   `__init__.py`, `constants.py`, `config.py`, `detectors.py`, `overlays.py`, `ui.py`, `gui.py`, `video_processor.py`, `main.py`: Core components of the censorship application.
    *   `models/`: Stores detection models (e.g., `face_detector.tflite`).
    *   `overlays/`: Directory for custom overlay images.
    *   `profiles/`: Stores configuration profiles.
    *   `output/`: Default directory for processed videos.
    *   `requirements.txt`: Project dependencies.
    *   `run.py`, `run_gui.py`: Entry points for CLI and GUI modes.
    *   `config.json`: Main configuration file.
    *   `tests/`: Unit tests for various modules.
*   **`ShoppingCalculator/`**: Contains the shopping list and tax calculation tool.
    *   `main.py`: Entry point for the application.
    *   `config.py`: Application configuration (taxes, directories).
    *   `menu.py`: Handles the main menu interface.
    *   `models.py`: Defines data structures (e.g., `ShoppingItem`).
    *   `taxes.py`: Calculates sales tax.
    *   `exports.py`: Handles receipt exporting.
    *   `storage.py`: Manages saving and loading shopping lists.
    *   `receipts.py`: Functions for displaying receipts.
    *   `utils.py`: Utility functions.
*   **`README.md`**: The main README for the repository.
*   **`LICENSE`**: The project's license file (GNU General Public License v3.0).

## Dependencies

*   **`adult_browser`**: PySide6, PySide6-Essentials, PySide6-Addons
*   **`adult_video_censorship`**: OpenCV, MediaPipe, Pillow, Ultralytics, NudeNet, tqdm, Pytest, Pytest-cov, CustomTkinter, imageio, imageio-ffmpeg
*   **`ShoppingCalculator`**: Rich (for enhanced console output)

## Contributing

Contributions are welcome! Please follow the guidelines outlined in the individual project's documentation or the general contributing guidelines if applicable. For the AutoCensorVideo project, please ensure:

1.  Code follows existing style and conventions.
2.  All functions have type hints and docstrings.
3.  Unit tests are added for new features.
4.  Configuration is validated.
5.  Logging is used instead of print statements.

## License

This project is licensed under the **GNU General Public License v3.0**. See the `LICENSE` file for more details.

## Important Links

*   **Repository**: [https://github.com/mrjohndowe/python_scripts](https://github.com/mrjohndowe/python_scripts)
*   **Author Profile**: [https://github.com/mrjohndowe](https://github.com/mrjohndowe)

---

Made with ❤️ by John Dowe | [**Fork**](https://github.com/mrjohndowe/python_scripts/fork) | [**Star**](https://github.com/mrjohndowe/python_scripts/stargazers) | [**Watch**](https://github.com/mrjohndowe/python_scripts/watchers) | [**Issues**](https://github.com/mrjohndowe/python_scripts/issues)


---
**<p align="center">Generated by [ReadmeCodeGen](https://www.readmecodegen.com/)</p>**
# MJD Python Scripts 🐍

A curated collection of Python scripts developed by MJD, encompassing a variety of utilities and applications.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0.html)

## Table of Contents

- [MJD Python Scripts 🐍](#mjd-python-scripts-)
  - [Table of Contents](#table-of-contents)
  - [Description 📝](#description-)
  - [Features ✨](#features-)
  - [Tech Stack 🛠️](#tech-stack-️)
  - [Installation 🚀](#installation-)
  - [Usage 💡](#usage-)
  - [Project Structure 📂](#project-structure-)
  - [Contributing 🤝](#contributing-)
  - [License 📄](#license-)
  - [Footer 🌐](#footer-)

## Description 📝

This repository, `python_scripts`, hosts a diverse set of Python scripts created by MJD. It includes applications like a shopping calculator with tax management and receipt generation, and a custom desktop browser for adult content websites. The project aims to provide practical tools and demonstrates various Python programming techniques.

## Features ✨

*   **Dowe Shopping Calculator:**
    *   Manages shopping lists with itemized prices and quantities.
    *   Calculates sales tax based on Colorado state, county, and city rates.
    *   Supports budget tracking and remaining balance calculation.
    *   Generates receipts in various formats (standard, store, detailed).
    *   Allows exporting receipts to TXT, CSV, and JSON files.
    *   Saves and loads shopping lists, and maintains a shopping history.
    *   Includes autosave functionality for ongoing lists.
*   **Adult Video Sidebar Desktop:**
    *   A standalone desktop browser application.
    *   Customizable dark interface with site shortcuts.
    *   Tabbed browsing with address bar, back/forward/reload functionality.
    *   Loads websites as top-level Chromium WebEngine pages, bypassing some iframe restrictions.

## Tech Stack 🛠️

*   **Languages:** Python, Markdown, JSON, Text
*   **Frameworks/Libraries:**
    *   **PySide6:** For the Adult Video Sidebar Desktop application (GUI).
    *   **Rich:** For enhanced console output in the Shopping Calculator.
*   **Build Tools:** PyInstaller (optional, for building EXE)

## Installation 🚀

**1. Dowe Shopping Calculator:**

This application uses standard Python libraries and the `rich` library. No external dependencies beyond Python 3.10+ are strictly required for basic functionality.

```bash
# No specific installation steps required, clone the repository and run directly.
# Ensure you have Python 3.10+ installed.
```

**2. Adult Video Sidebar Desktop:**

This application requires PySide6. It's recommended to use a virtual environment.

```bash
# Navigate to the adult_browser directory
cd adult_browser

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage 💡

**1. Dowe Shopping Calculator:**

The entry point for the Shopping Calculator is `ShoppingCalculator/main.py`.

```bash
# Navigate to the root of the repository
cd python_scripts

# Run the Shopping Calculator
python ShoppingCalculator/main.py
```

Upon running, you will be presented with a splash screen and the main menu, offering options to add items, manage your cart, print receipts, export data, and more.

**2. Adult Video Sidebar Desktop:**

The entry point is `adult_browser/adult_video_sidebar.py`.

```bash
# Navigate to the adult_browser directory
cd adult_browser

# Run the application
python adult_video_sidebar.py
```

This will launch the desktop browser application. You can use the predefined site shortcuts, the address bar to navigate to any website, and the built-in tab management features.

**Building an EXE (Optional for Adult Video Sidebar):**

To create a standalone executable for Windows:

```powershell
# Ensure you are in the adult_browser directory and have PyInstaller installed
pip install pyinstaller

# Build the executable
py -m PyInstaller --noconsole --onedir --name AdultVideoSidebar adult_video_sidebar.py
```

The executable will be located in the `dist/AdultVideoSidebar` folder.

## Project Structure 📂

```
python_scripts/
├── adult_browser/
│   ├── adult_video_sidebar.py
│   ├── README.md
│   └── requirements.txt
├── ShoppingCalculator/
│   ├── config.py
│   ├── data/
│   │   ├── autosave.json
│   │   └── settings.json
│   ├── exports.py
│   ├── history.py
│   ├── main.py
│   ├── menu.py
│   ├── models.py
│   ├── receipts.py
│   ├── storage.py
│   ├── taxes.py
│   └── utils.py
├── LICENSE
├── README.md
└── scriptsInstall.ps1
```

## Contributing 🤝

Contributions are welcome! Please feel free to:

*   Fork the repository.
*   Create a new branch (`git checkout -b feature/your-feature-name`).
*   Make your changes.
*   Commit your changes (`git commit -m 'Add some feature'`).
*   Push to the branch (`git push origin feature/your-feature-name`).
*   Open a Pull Request.

Please ensure your code adheres to Python best practices and includes relevant documentation.

## License 📄

This project is licensed under the **GNU General Public License v3.0**. See the `LICENSE` file for more details.

## Footer 🌐

**Repository:** [python_scripts](https://github.com/mrjohndowe/python_scripts)
**Author:** MJD (John Dowe)
**Contact:** [mrjohndowe@gmail.com](mailto:mrjohndowe@gmail.com)

*Feel free to fork, star, and contribute to this project! Your support is greatly appreciated.* :star:


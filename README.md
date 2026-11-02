# Dowe Shopping Calculator 🛒

A Python-based command-line application designed to help users manage shopping lists, calculate sales tax, and track expenses with detailed receipt generation.

## Repository

*   **Name:** python_scripts
*   **Description:** A collection of MJD Python Scripts
*   **Primary Language:** Python
*   **Stars:** 0 ⭐
*   **Forks:** 0 🍴
*   **License:** GNU General Public License v3.0
*   **URL:** [https://github.com/mrjohndowe/python_scripts](https://github.com/mrjohndowe/python_scripts)

## Table of Contents 📜

*   [Project Title & Badges](#project-title--badges)
*   [Description](#description)
*   [Table of Contents](#table-of-contents-)
*   [Features](#features-)
*   [Tech Stack](#tech-stack-)
*   [Installation](#installation-)
*   [Usage](#usage-)
*   [Project Structure](#project-structure-)
*   [Contributing](#contributing-)
*   [License](#license-)
*   [Important Links](#important-links-)
*   [Footer](#footer-)

## Features 🚀

*   **Shopping List Management:** Add, remove, edit items in your shopping list.
*   **Budget Tracking:** Set a budget and track remaining funds.
*   **Sales Tax Calculation:** Automatic calculation of state, county, and city sales tax for Pueblo, Colorado.
*   **Multiple Receipt Formats:** Generate receipts in standard, store-style, and detailed formats.
*   **Export Options:** Export shopping lists and receipts to TXT, CSV, and JSON formats.
*   **Shopping History:** Save and load past shopping lists and view history.
*   **Autosave:** Automatically saves the current shopping list and budget.
*   **Interactive CLI:** User-friendly command-line interface with `rich` library for enhanced visuals.

## Tech Stack 💻

*   **Language:** Python
*   **Libraries:** `rich` (for enhanced CLI output), `PySide6` (for Adult Browser)
*   **Frameworks:** None explicitly detected for the Shopping Calculator, plain Python.

## Installation 📥

**1. Clone the Repository:**
```bash
git clone https://github.com/mrjohndowe/python_scripts.git
cd python_scripts
```

**2. Navigate to the Shopping Calculator Directory:**
```bash
cd ShoppingCalculator
```

**3. Install Dependencies:**

This project utilizes the `rich` library. You can install it using pip:

```bash
pip install rich
```

**4. Run the Application:**

Execute the main script:

```bash
python main.py
```

## Usage 💡

The `Dowe Shopping Calculator` is designed for ease of use via a text-based interface. Upon running `main.py`, you will be greeted with a splash screen and then presented with a menu.

### Main Menu Options:

*   **Add Item:** Add new items to your shopping list, including their price and quantity.
*   **Remove Item:** Remove items from the current list.
*   **Edit Item:** Modify the details of existing items.
*   **Shopping Cart:** View the current items in your shopping cart.
*   **Print Receipt:** Display a formatted receipt of your current shopping list with tax calculations.
*   **Save Shopping List:** Save your current shopping list to a file for later use.
*   **Load Shopping List:** Load a previously saved shopping list.
*   **Shopping History:** View a history of past shopping transactions.
*   **Export Receipt:** Export the current receipt in TXT, CSV, or JSON format.
*   **Settings:** (Functionality may be incomplete based on analysis)
*   **Statistics:** (Functionality may be incomplete based on analysis)
*   **Exit:** Close the application.

### Example Workflow:

1.  Run `python main.py`.
2.  Choose '1' to add an item (e.g., 'Milk', Price: $3.50, Quantity: 2).
3.  Add more items.
4.  Choose '4' to view your Shopping Cart.
5.  Choose '5' to print a standard receipt.
6.  Choose '9' to export the receipt as a CSV file.
7.  Choose '0' to exit.

### Pueblo, Colorado Sales Tax:

The calculator is pre-configured with the sales tax rates for Pueblo, Colorado:

*   State Tax: 2.9%
*   County Tax: 1.0%
*   City Tax: 3.7%

These rates are automatically applied to your subtotals.

### Adult Browser (Separate Application):

This repository also contains a separate application, `adult_browser/adult_video_sidebar.py`, which functions as a standalone desktop browser. To run it:

1.  Navigate to the `adult_browser` directory.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Run the application: `py adult_video_sidebar.py` (on Windows) or `python adult_video_sidebar.py` (on other OS).

This application is not integrated with the shopping calculator and serves a distinct purpose.

## Project Structure 📂

```
python_scripts/
├── adult_browser/
│   ├── __init__.py
│   ├── adult_video_sidebar.py
│   └── requirements.txt
│   └── README.md
├── ShoppingCalculator/
│   ├── __init__.py
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
└── README.md
```

## Contributing 🤝

Contributions are welcome! Please feel free to:

*   Fork the repository.
*   Create a new branch for your feature (`git checkout -b feature/AmazingFeature`).
*   Commit your changes (`git commit -m 'Add some AmazingFeature'`).
*   Push to the branch (`git push origin feature/AmazingFeature`).
*   Open a Pull Request.

Please read the CONTRIBUTING.md file (if available) for more details on our code of conduct and the process for submitting pull requests.

## License 📄

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for more details.

## Important Links 🔗

*   **Repository:** [https://github.com/mrjohndowe/python_scripts](https://github.com/mrjohndowe/python_scripts)
*   **Author:** [mrjohndowe](https://github.com/mrjohndowe)

## Footer 👋

[![GitHub stars](https://img.shields.io/github/stars/mrjohndowe/python_scripts?style=social)](https://github.com/mrjohndowe/python_scripts/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/mrjohndowe/python_scripts?style=social)](https://github.com/mrjohndowe/python_scripts/fork)

--- 

**Repository:** `python_scripts`
**URL:** [https://github.com/mrjohndowe/python_scripts](https://github.com/mrjohndowe/python_scripts)
**Author:** [mrjohndowe](https://github.com/mrjohndowe)

Feel free to **fork**, **star ⭐**, and **open issues** if you encounter any problems or have suggestions!


---
**<p align="center">Generated by [ReadmeCodeGen](https://www.readmecodegen.com/)</p>**
"""User interface functions for AutoCensorVideo."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from autocensor.config import Config, OverlaySettings
from autocensor.constants import SUPPORTED_VIDEO


def select_video() -> Path | None:
    """Select exactly one video using a file picker.

    Returns:
        Path to selected video or None if cancelled.
    """
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    filename = filedialog.askopenfilename(
        title="AutoCensorVideo - Select ONE video",
        filetypes=[
            ("Video files", SUPPORTED_VIDEO),
            ("All files", "*.*")
        ]
    )

    root.destroy()

    if not filename:
        return None

    return Path(filename)


def select_videos() -> list[Path]:
    """Select multiple videos using a file picker.

    Returns:
        List of paths to selected videos.
    """
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    filenames = filedialog.askopenfilenames(
        title="AutoCensorVideo - Select videos",
        filetypes=[
            ("Video files", SUPPORTED_VIDEO),
            ("All files", "*.*")
        ]
    )

    root.destroy()

    if not filenames:
        return []

    return [Path(f) for f in filenames]


def select_censoring_method(region_name: str) -> dict[str, Any] | str:
    """Ask user how they want to censor a specific region.

    Args:
        region_name: Name of the region (e.g., "Face", "Private parts").

    Returns:
        Dictionary with overlay settings or overlay type string.
    """
    print(f"\n{region_name} censoring options:")
    print("1. Blur")
    print("2. Pixelate")
    print("3. Emoji")
    print("4. Black box")
    print("5. Custom image")

    while True:
        choice = input(f"Select {region_name} censoring method (1-5): ").strip()

        if choice == "1":
            print("\nBlur strength options (higher = more blurry):")
            print("  15: Light blur (features still somewhat visible)")
            print("  31: Medium blur (features heavily obscured)")
            print("  51: Heavy blur (completely indistinguishable)")
            print("  71: Very heavy blur (large smear)")
            while True:
                strength = input("Enter blur strength (3-100, default 31): ").strip()
                if not strength:
                    strength = "31"
                try:
                    strength_val = int(strength)
                    if 3 <= strength_val <= 100:
                        return {"type": "blur", "strength": strength_val}
                    else:
                        print("Strength must be between 3 and 100.")
                except ValueError:
                    print("Please enter a valid number.")
        elif choice == "2":
            print("\nPixelate strength options (higher = larger blocks):")
            print("  10: Small blocks (some detail visible)")
            print("  18: Medium blocks (features obscured)")
            print("  30: Large blocks (completely pixelated)")
            while True:
                strength = input("Enter pixelate strength (2-100, default 18): ").strip()
                if not strength:
                    strength = "18"
                try:
                    strength_val = int(strength)
                    if 2 <= strength_val <= 100:
                        return {"type": "pixelate", "strength": strength_val}
                    else:
                        print("Strength must be between 2 and 100.")
                except ValueError:
                    print("Please enter a valid number.")
        elif choice == "3":
            emoji = input("Enter emoji (e.g., 😎, 🍑): ").strip()
            return {"type": "emoji", "emoji": emoji}
        elif choice == "4":
            return "box"
        elif choice == "5":
            image_path = input("Enter image path: ").strip()
            return {"type": "image", "image": image_path}
        else:
            print("Invalid choice. Please enter 1-5.")


def configure_censoring(config: Config) -> Config:
    """Ask user how they want to censor faces and private parts.

    Args:
        config: Current configuration.

    Returns:
        Updated configuration.
    """
    print("\n================================")
    print("CENSORING CONFIGURATION")
    print("================================")

    face_method = select_censoring_method("Face")

    if isinstance(face_method, dict):
        config["overlay"]["face"].update(face_method)
    else:
        config["overlay"]["face"]["type"] = face_method

    private_method = select_censoring_method("Private parts")

    if isinstance(private_method, dict):
        config["overlay"]["private"].update(private_method)
    else:
        config["overlay"]["private"]["type"] = private_method

    return config


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    """Ask a yes/no question.

    Args:
        prompt: Question to ask.
        default: Default answer if user just presses Enter.

    Returns:
        True for yes, False for no.
    """
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{prompt} ({default_str}): ").strip().lower()
        if not response:
            return default
        if response in ("y", "yes"):
            return True
        if response in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")


def ask_choice(prompt: str, options: list[str], default: int | None = None) -> int:
    """Ask user to choose from a list of options.

    Args:
        prompt: Question to ask.
        options: List of option strings.
        default: Default option index (0-based) if user just presses Enter.

    Returns:
        Index of selected option.
    """
    for i, option in enumerate(options):
        print(f"  {i + 1}. {option}")

    while True:
        default_str = f" (default: {default + 1})" if default is not None else ""
        response = input(f"{prompt} [1-{len(options)}]{default_str}: ").strip()

        if not response and default is not None:
            return default

        try:
            choice = int(response) - 1
            if 0 <= choice < len(options):
                return choice
            print(f"Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print("Please enter a valid number.")


def select_profile() -> str | None:
    """Ask user to select a configuration profile.

    Returns:
        Profile name or None if cancelled.
    """
    from autocensor.config import list_profiles

    profiles = list_profiles()

    if not profiles:
        print("No profiles available.")
        return None

    print("\nAvailable profiles:")
    for i, profile in enumerate(profiles):
        print(f"  {i + 1}. {profile}")

    print(f"  {len(profiles) + 1}. Cancel")

    while True:
        try:
            choice = input(f"Select profile [1-{len(profiles) + 1}]: ").strip()
            if not choice:
                return None

            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(profiles):
                return profiles[choice_idx]
            elif choice_idx == len(profiles):
                return None
            else:
                print(f"Please enter a number between 1 and {len(profiles) + 1}.")
        except ValueError:
            print("Please enter a valid number.")

import sys
import subprocess
import importlib.util
from pathlib import Path

PACKAGE = "cryptography"


def ensure_package(package_name):
    if importlib.util.find_spec(package_name) is None:
        print(f"'{package_name}' is not installed.")
        print(f"Installing {package_name}...\n")

        try:
            subprocess.check_call([
                sys.executable,
                "-m",
                "pip",
                "install",
                package_name
            ])
        except subprocess.CalledProcessError:
            print(f"Failed to install {package_name}.")
            input("Press Enter to exit...")
            sys.exit(1)


ensure_package(PACKAGE)

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def prompt_output_path(prompt):
    while True:
        path = input(prompt).strip().strip('"')

        if not path:
            print("Please enter a filename.\n")
            continue

        output = Path(path)

        if output.parent != Path():
            output.parent.mkdir(parents=True, exist_ok=True)

        return output


def prompt_input_file():
    while True:
        path = input("Enter the path to the private key: ").strip().strip('"')

        if not path:
            print("Please enter a file path.\n")
            continue

        file = Path(path)

        if not file.exists():
            print("File does not exist.\n")
            continue

        if file.is_dir():
            print("That is a folder, not a file.\n")
            continue

        return file


def generate_new_key():
    print("\n=== Generate New PKCS#8 RSA Key ===\n")

    output = prompt_output_path(
        "Save private key as (example: keys/private_key.pem): "
    )

    public_output = output.with_name(output.stem + "_public.pem")

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )

    with open(output, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(public_output, "wb") as f:
        f.write(
            private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    print("\nSuccess!")
    print(f"Private Key : {output}")
    print(f"Public Key  : {public_output}")


def convert_existing_key():
    print("\n=== Convert Existing Key to PKCS#8 ===\n")

    input_file = prompt_input_file()

    output_file = prompt_output_path(
        "Save converted key as (example: keys/private_key.pem): "
    )

    with open(input_file, "rb") as f:
        key_data = f.read()

    try:
        private_key = serialization.load_pem_private_key(
            key_data,
            password=None,
        )
    except Exception as e:
        print(f"\nUnable to load the private key.\n\n{e}")
        input("\nPress Enter to exit...")
        sys.exit(1)

    with open(output_file, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    print("\nConversion completed successfully!")
    print(f"Input : {input_file}")
    print(f"Output: {output_file}")


def main():
    while True:
        print("\n==============================")
        print(" PKCS#8 RSA Key Utility")
        print("==============================")
        print("1) Generate a new RSA key pair")
        print("2) Convert an existing private key to PKCS#8")
        print("3) Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            generate_new_key()
            break

        elif choice == "2":
            convert_existing_key()
            break

        elif choice == "3":
            sys.exit(0)

        else:
            print("\nInvalid selection.\n")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()

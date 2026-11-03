# mkdir AutoCensorVideo
# cd AutoCensorVideo

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install opencv-python mediapipe Pillow ultralytics

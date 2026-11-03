# mkdir AutoCensorVideo
# cd AutoCensorVideo

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

New-Item -ItemType Directory -Force .\models | Out-Null

Invoke-WebRequest `
  -Uri "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite" `
  -OutFile ".\models\face_detector.tflite"

python .\AutoCensorVideo.py

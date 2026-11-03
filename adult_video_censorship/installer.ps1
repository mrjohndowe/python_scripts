# mkdir AutoCensorVideo
# cd AutoCensorVideo

if ($env:VIRTUAL_ENV) {
    Write-Host "Virtual environment is active: $env:VIRTUAL_ENV" -ForegroundColor Green
    deactivate
    Remove-Item -Recurse -Force .venv
} else {
    Write-Host "Virtual environment is NOT active" -ForegroundColor Yellow
    py -3.12 -m venv .venv

    .\.venv\Scripts\Activate.ps1

    python -m pip install --upgrade pip

    python -m pip install -r requirements.txt

    New-Item -ItemType Directory -Force .\models | Out-Null

    Invoke-WebRequest `
    -Uri "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite" `
    -OutFile ".\models\face_detector.tflite"

    python .\AutoCensorVideo.py
}

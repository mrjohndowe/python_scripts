# AutoCensorVideo - Build and Test Commands

This file contains commands for building, testing, and verifying the AutoCensorVideo project.

## Environment Setup

### Create Virtual Environment
```powershell
py -3.14 -m venv .venv
```

### Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Install Development Dependencies (for testing)
```powershell
pip install pytest pytest-cov
```

## Running the Application

### Main Application
```powershell
python .\run.py
```

### Alternative (using old script)
```powershell
python .\AutoCensorVideo.py
```

## Testing

### Run All Tests
```powershell
python -m pytest tests/
```

### Run Tests with Verbose Output
```powershell
python -m pytest tests/ -v
```

### Run Tests with Coverage
```powershell
python -m pytest tests/ --cov=autocensor --cov-report=html
```

### Run Tests with Coverage in Terminal
```powershell
python -m pytest tests/ --cov=autocensor --cov-report=term
```

### Run Specific Test File
```powershell
python -m pytest tests/test_config.py
```

### Run Specific Test Function
```powershell
python -m pytest tests/test_config.py::test_default_config_structure
```

## Code Quality

### Type Checking (if mypy is installed)
```powershell
pip install mypy
mypy autocensor/
```

### Linting (if pylint is installed)
```powershell
pip install pylint
pylint autocensor/
```

### Format Checking (if black is installed)
```powershell
pip install black
black --check autocensor/
```

### Auto-format Code (if black is installed)
```powershell
black autocensor/
```

## FFmpeg Verification

### Check FFmpeg Installation
```powershell
ffmpeg -version
ffprobe -version
```

## Model Setup

### Download Face Detection Model
```powershell
New-Item -ItemType Directory -Force .\models
Invoke-WebRequest `
  -Uri "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite" `
  -OutFile ".\models\face_detector.tflite"
```

### Download NudeNet 640m Model (Optional, for higher accuracy)
```powershell
Invoke-WebRequest `
  -Uri "https://github.com/notAI-tech/NudeNet/releases/download/v0/detector_640m.onnx" `
  -OutFile ".\models\nudenet_640m.onnx"
```

## Directory Structure

### Create Required Directories
```powershell
New-Item -ItemType Directory -Force .\models
New-Item -ItemType Directory -Force .\output
New-Item -ItemType Directory -Force .\overlays
New-Item -ItemType Directory -Force .\profiles
```

## Configuration

### Generate Default Configuration
```powershell
python -c "from autocensor.config import load_config; load_config()"
```

### Validate Current Configuration
```powershell
python -c "from autocensor.config import load_config, validate_config; config = load_config(); errors = validate_config(config); print('Errors:', errors if errors else 'None')"
```

## Troubleshooting

### Check Python Version
```powershell
python --version
```

### Check Installed Packages
```powershell
pip list
```

### Check for Package Conflicts
```powershell
pip check
```

### Reinstall All Dependencies
```powershell
pip install --force-reinstall -r requirements.txt
```

## Cleanup

### Remove Virtual Environment
```powershell
Remove-Item -Recurse -Force .\.venv
```

### Clean Output Directory
```powershell
Remove-Item -Recurse -Force .\output\*
```

### Clean Cache Files
```powershell
Remove-Item -Recurse -Force .\__pycache__
Remove-Item -Recurse -Force .\autocensor\__pycache__
Remove-Item -Recurse -Force .\tests\__pycache__
```

## Performance Testing

### Process a Test Video (replace with actual video path)
```powershell
python .\run.py
# Select a short test video
# Choose "Preview mode" for quick testing
```

### Benchmark Processing Speed
```powershell
# Use a short video and check the processing statistics output
# Look for "Average processing speed" in the statistics
```

## Development Workflow

### Typical Development Cycle
1. Make code changes
2. Run tests: `python -m pytest tests/ -v`
3. Run type checking: `mypy autocensor/`
4. Test manually: `python .\run.py`
5. Commit changes

### Adding New Features
1. Create feature branch
2. Implement feature with type hints and docstrings
3. Add unit tests
4. Update README if needed
5. Run full test suite
6. Create pull request

## Notes

- Python 3.14 is required
- Windows 10/11 is the primary supported platform
- FFmpeg must be in system PATH
- MediaPipe face model must be downloaded separately
- NudeNet is included in requirements.txt
- Tests use pytest framework
- Coverage reports are generated in htmlcov/ directory

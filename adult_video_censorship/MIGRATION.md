# Migration Guide - v1.0 to v2.0

This guide helps you migrate from the old monolithic AutoCensorVideo.py to the new modular v2.0 architecture.

## What Changed

### New Project Structure

The old `AutoCensorVideo.py` (950 lines) has been split into modular components:

```
autocensor/
├── __init__.py          # Package initialization
├── constants.py         # All constants and configuration values
├── config.py            # Configuration management with validation
├── detectors.py         # Face and private-region detectors
├── overlays.py          # Overlay rendering functions
├── video_processor.py   # Video processing with FFmpeg
├── ui.py                # User interface functions
└── main.py              # Main application entry point
```

### New Entry Point

**Old:**
```powershell
python .\AutoCensorVideo.py
```

**New:**
```powershell
python .\run.py
```

The old `AutoCensorVideo.py` is still present for backward compatibility, but using `run.py` is recommended.

## Migration Steps

### 1. Update Dependencies

The new version has pinned dependencies. Reinstall to ensure compatibility:

```powershell
pip install -r requirements.txt
```

New dependencies added:
- `tqdm==4.67.1` - Progress bars
- `pytest==8.3.4` - Testing framework
- `pytest-cov==6.0.0` - Test coverage

### 2. Verify Configuration

Your existing `config.json` will work with the new version. The configuration loader automatically:

- Fills in missing values with defaults
- Validates configuration on load
- Reports any validation errors as warnings

No manual changes required, but you may see validation warnings if your config has issues.

### 3. Update Overlay Image Paths (Recommended)

If you use custom image overlays with absolute paths, consider making them portable:

**Old (absolute path):**
```json
{
  "type": "image",
  "image": "C:\\Users\\Name\\Pictures\\overlay.png"
}
```

**New (relative path):**
```json
{
  "type": "image",
  "image": "overlays/overlay.png"
}
```

Place your overlay images in the `overlays/` directory.

### 4. Try New Features

The new version offers several new features:

#### Batch Processing
1. Run `python .\run.py`
2. Select "Batch processing" mode
3. Select multiple videos
4. They will be processed sequentially

#### Preview Mode
1. Run `python .\run.py`
2. Select "Preview mode"
3. Select a video
4. First 30 seconds processed with frame skip for quick testing

#### Configuration Profiles
1. Run `python .\run.py`
2. Select "Configuration only" mode
3. Choose "Save current configuration as profile"
4. Enter a profile name
5. Load profiles later from the same menu

#### Detection Export
When processing a video, you'll be asked:
"Export detection boxes to JSON?"

Answer "y" to save detection data to `output/<video-name>_detections.json`

## Configuration Changes

### New Configuration Options

The following new options are available (use defaults if not specified):

- `profiles/` directory for configuration profiles
- `overlays/` directory for portable overlay images
- Logging system (no configuration needed, uses INFO level by default)

### Configuration Validation

The new version validates your configuration on load. Common issues:

- `confidence` must be between 0 and 1
- `opacity` must be between 0 and 1
- `padding` must be between 0 and 1
- `color` must be a list of 3 integers (0-255)
- Overlay type must be one of: blur, pixelate, emoji, box, image

If you see validation warnings, fix the reported issues in `config.json`.

## Behavior Changes

### Logging Instead of Print

The new version uses Python's logging system instead of print statements. This provides:

- Timestamps on all messages
- Log levels (INFO, WARNING, ERROR)
- Better debugging capability

Log output format:
```
2024-11-02 12:34:56 - autocensor.video_processor - INFO - Processing video: test.mp4
```

### Graceful Degradation

If one detector fails (e.g., NudeNet initialization fails), the other detector continues working. You'll see a warning but processing won't stop.

### FFmpeg Retry Logic

FFmpeg operations now automatically retry up to 3 times with a 2-second delay between attempts. This handles transient FFmpeg errors.

### Progress Bar

Video processing now shows a progress bar:
```
Processing frames: 100%|██████████| 300/300 [00:15<00:00, 20.0frames/s]
```

### Processing Statistics

After processing, you'll see detailed statistics:
```
================================
PROCESSING STATISTICS
================================
Total frames processed: 300
Faces detected: 45
Private regions detected: 12
Processing time: 15.23s
Average processing speed: 19.70 FPS
================================
```

## Running Tests

The new version includes unit tests. Run them:

```powershell
python -m pytest tests/ -v
```

With coverage:
```powershell
python -m pytest tests/ --cov=autocensor --cov-report=html
```

## Troubleshooting

### Import Errors

If you see import errors:

```powershell
ModuleNotFoundError: No module named 'autocensor'
```

Solution: Make sure you're running from the project root directory and using `python .\run.py`.

### Configuration Validation Errors

If you see validation warnings on startup:

1. Check the specific error messages
2. Fix the reported issues in `config.json`
3. Restart the application

### Missing Dependencies

If you see errors about missing packages:

```powershell
pip install -r requirements.txt
```

## Rollback

If you need to use the old version:

```powershell
python .\AutoCensorVideo.py
```

The old file is still present and functional.

## API Changes (for Developers)

If you were importing from AutoCensorVideo.py:

**Old:**
```python
from AutoCensorVideo import load_config, process_video
```

**New:**
```python
from autocensor.config import load_config
from autocensor.video_processor import VideoProcessor
from autocensor.detectors import FaceDetector, PrivateDetector
```

See the individual module files for updated function signatures and documentation.

## Support

For issues or questions:

1. Check the updated README.md for detailed documentation
2. Check AGENTS.md for build and test commands
3. Review the troubleshooting section in README.md
4. Check logs for detailed error information

## Summary of Improvements

✅ Modular architecture (8 modules instead of 1 monolithic file)
✅ Comprehensive type hints
✅ Complete docstrings
✅ Logging system
✅ Pinned dependencies
✅ Progress bars
✅ Batch processing
✅ Preview mode
✅ Configuration profiles
✅ Detection export to JSON
✅ Processing statistics
✅ Portable overlay paths
✅ Configuration validation
✅ Graceful degradation
✅ FFmpeg retry logic
✅ Constants defined
✅ Cross-platform emoji support
✅ Unit tests
✅ Comprehensive documentation
✅ GPU acceleration documentation

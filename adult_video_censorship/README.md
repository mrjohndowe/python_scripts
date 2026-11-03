# AutoCensorVideo

Advanced video censorship utility for Windows with modular architecture, batch processing, and comprehensive configuration options.

## Features

### Core Features
- **Multiple Processing Modes**: Single video, batch processing, preview mode, and configuration-only mode
- **Face Detection**: MediaPipe Tasks face detector with high accuracy
- **Private-Region Detection**: NudeNet pre-trained nudity detection (no custom training required) or custom YOLO models
- **Multiple Overlay Types**: Blur, pixelation, emoji, solid box, or custom image overlays
- **Configurable Settings**: Fine-tune detection confidence, overlay strength, padding, opacity, and more
- **Original Video Preservation**: Always creates a new censored copy
- **Audio Preservation**: Copies audio from original video

### New Features (v2.0)
- **Modern GUI**: CustomTkinter-based graphical user interface with dark theme
- **Video Preview**: Built-in video player with playback controls
- **Batch Processing**: Process multiple videos in one session
- **Preview Mode**: Test detections quickly without full encoding
- **Progress Bars**: Real-time progress indication with tqdm
- **Processing Statistics**: View faces detected, private regions, processing time, and FPS
- **Configuration Profiles**: Save and load different censorship configurations
- **Detection Export**: Export detection boxes to JSON for analysis
- **Frame Skip Option**: Skip frames for faster preview processing
- **Portable Overlay Paths**: Use relative paths for overlay images
- **Logging System**: Comprehensive logging for debugging
- **Configuration Validation**: Automatic validation of config settings
- **Graceful Degradation**: Continues processing if one detector fails
- **FFmpeg Retry Logic**: Automatic retries for FFmpeg operations
- **Cross-Platform Emoji Support**: Automatic font detection for emoji rendering
- **Modular Architecture**: Clean separation of concerns for maintainability

## Requirements

- Windows 10 or Windows 11
- Python 3.14, 64-bit
- FFmpeg and FFprobe
- MediaPipe face detection model

### Additional Requirements for GUI Mode

- CustomTkinter (included in requirements.txt)
- imageio (for video preview in GUI)

## Installation

Open PowerShell in this project folder.

Create the virtual environment:

```powershell
py -3.14 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## FFmpeg

Install FFmpeg and make sure both commands work:

```powershell
ffmpeg -version
ffprobe -version
```

## Face Detection Model

Create the models folder:

```powershell
New-Item -ItemType Directory -Force .\models
```

Download the face detector:

```powershell
Invoke-WebRequest `
  -Uri "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite" `
  -OutFile ".\models\face_detector.tflite"
```

## Running the Application

You can run AutoCensorVideo in two modes:

### GUI Mode (Recommended)

Launch the modern graphical user interface:

```powershell
python .\run_gui.py
```

The GUI features:
- **Video Preview**: Built-in video player with playback controls
- **Configuration Editor**: Real-time configuration editing with sliders
- **Detection Statistics**: Live display of detection counts and confidence
- **Progress Visualization**: Real-time progress bar during processing
- **File Browser**: Easy video selection
- **Profile Management**: Save and load configuration profiles
- **Dark Theme**: Modern, professional appearance

### CLI Mode

For command-line usage:

```powershell
python .\run.py
```

### Processing Modes

When you run the CLI application, you'll see a mode selection menu:

1. **Single Video**: Process one video at a time
2. **Batch Processing**: Select and process multiple videos sequentially
3. **Preview Mode**: Process a sample of the video quickly to test detections
4. **Configuration Only**: Modify, save, or load configuration profiles

### GUI Mode Features

The GUI provides a modern, user-friendly interface:

- **Sidebar**: Quick access to file selection, batch processing, and profiles
- **Video Preview**: Built-in video player with play/pause and frame scrubbing
- **Detection Statistics**: Real-time display of faces and private regions detected
- **Configuration Editor**: Interactive sliders for overlay settings
- **Progress Bar**: Visual progress indication during processing
- **Profile Management**: Load and save configuration profiles
- **Dark Theme**: Modern, professional appearance with CustomTkinter

### Output

Censored videos are saved to:

```
output\<video-name>_censored.mp4
```

Detection exports (if enabled) are saved to:

```
output\<video-name>_detections.json
```

## Configuration

The main configuration file is `config.json`. You can edit it directly or use the configuration mode in the application.

### Configuration Profiles

Save different censorship settings as profiles:

1. Run the application and select "Configuration only" mode
2. Choose "Save current configuration as profile"
3. Enter a profile name
4. Profiles are saved in the `profiles/` directory

Load a profile:

1. Run the application and select "Configuration only" mode
2. Choose "Load configuration profile"
3. Select from available profiles

### Overlay Settings

Edit `config.json` to customize overlays. Supported overlay types:

- **blur**: Gaussian blur
- **pixelate**: Block-based pixelation
- **emoji**: Emoji overlay
- **box**: Solid color box
- **image**: Custom image overlay

#### Overlay Configuration Options

- `type`: Overlay type (blur, pixelate, emoji, box, image)
- `emoji`: Emoji character (for emoji type)
- `image`: Path to overlay image (for image type)
- `strength`: Blur kernel size or pixelation block size (3-100)
- `padding`: Expand detection area (0.0-1.0, default 0.15)
- `opacity`: Overlay opacity (0.0-1.0, default 1.0)
- `scale`: Resize overlay relative to detection box (default 1.0)
- `color`: RGB color for box overlay [R, G, B]

#### Example Configurations

**Blur overlay:**
```json
{
  "type": "blur",
  "strength": 31,
  "padding": 0.15,
  "opacity": 1.0
}
```

**Pixelate overlay:**
```json
{
  "type": "pixelate",
  "strength": 18,
  "padding": 0.15,
  "opacity": 1.0
}
```

**Emoji overlay:**
```json
{
  "type": "emoji",
  "emoji": "🍑",
  "padding": 0.15,
  "opacity": 1.0
}
```

**Black box overlay:**
```json
{
  "type": "box",
  "color": [0, 0, 0],
  "padding": 0.15,
  "opacity": 1.0
}
```

**Custom image overlay:**
```json
{
  "type": "image",
  "image": "overlays/censor.png",
  "padding": 0.15,
  "opacity": 1.0
}
```

### Configuration Options

- `face_detection`: Enable/disable face detection (true/false)
- `private_detection`: Enable/disable private-region detection (true/false)
- `face_model`: Path to face detection model
- `private_model`: Path to private-region detection model
- `private_detector_type`: "nudenet" or "yolo"
- `private_class_ids`: List of YOLO class IDs to detect
- `private_labels`: List of NudeNet labels to detect
- `private_confidence`: Private-region detection confidence threshold (0.0-1.0)
- `confidence`: Face detection confidence threshold (0.0-1.0)
- `detect_every_n_frames`: Detection interval in frames (default: 2)

### Encoding Options

- `codec`: Video codec (default: libx264)
- `crf`: Quality setting (0-51, lower = better quality, default: 20)
- `preset`: Encoding speed/quality (ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)
- `audio`: Audio codec (default: copy)

## Private-Region Detection

### Option 1: NudeNet (Recommended)

NudeNet is a pre-trained nudity detection model that recognizes anatomical regions out of the box. No custom training required.

Configuration:

```json
{
  "private_detector_type": "nudenet",
  "private_labels": [
    "FEMALE_BREAST_EXPOSED",
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
    "BUTTOCKS_EXPOSED",
    "ANUS_EXPOSED"
  ],
  "private_confidence": 0.35
}
```

NudeNet is included in requirements.txt and will use the bundled 320n model by default. For higher accuracy, download the 640m model and set:

```json
{
  "private_model": "models/nudenet_640m.onnx"
}
```

### Option 2: Custom YOLO Model

Requires a compatible custom-trained YOLO model.

Place it here:

```
models\private_regions.pt
```

Configuration:

```json
{
  "private_detector_type": "yolo",
  "private_class_ids": [0, 1, 2]
}
```

The model must recognize the regions you want censored. A general object detector does not automatically recognize private anatomical regions.

## Overlay Images

Place custom overlay images in the `overlays/` directory for use with the "image" overlay type. This makes paths portable across different systems.

Supported formats: PNG, JPG, JPEG, BMP, GIF

PNG images with transparency are recommended.

## Processing Statistics

After processing, you'll see statistics including:

- Total frames processed
- Number of faces detected
- Number of private regions detected
- Processing time
- Average processing speed (FPS)

## Preview Mode

Preview mode processes a sample of the video (first 30 seconds with frame skip) to quickly test detection accuracy without full encoding. This is useful for:

- Testing new detector configurations
- Checking if detection confidence is appropriate
- Verifying overlay settings before full processing

Note: Preview mode creates an intermediate file. Process normally for the final MP4.

## Batch Processing

Batch processing allows you to select multiple videos and process them sequentially with the same configuration. This is useful for:

- Processing entire folders of videos
- Applying consistent censorship settings across multiple files
- Automating workflows

## Troubleshooting

### FFmpeg not found

**Error**: "FFmpeg was not found in PATH"

**Solution**:
1. Install FFmpeg from https://ffmpeg.org/download.html
2. Add FFmpeg to your system PATH
3. Restart PowerShell
4. Verify with `ffmpeg -version`

### Face detection model missing

**Error**: "Face detection model missing"

**Solution**:
1. Create the models directory: `New-Item -ItemType Directory -Force .\models`
2. Download the model using the command in the README
3. Verify the file exists in the models directory

### NudeNet initialization failed

**Error**: "NudeNet initialization failed"

**Solution**:
1. Ensure nudenet is installed: `pip install nudenet==3.4.2`
2. Check that the model path is correct
3. Try using the default model (remove `private_model` from config)
4. Check logs for detailed error information

### YOLO model not found

**Error**: "Private-region model not found"

**Solution**:
1. Place your custom YOLO model in `models/private_regions.pt`
2. Update the path in config.json if using a different location
3. Or switch to NudeNet by setting `private_detector_type` to "nudenet"

### Video processing failed

**Error**: "Could not open selected video" or processing errors

**Solution**:
1. Verify the video file exists and is not corrupted
2. Ensure the video format is supported (mp4, mkv, mov, avi, webm, m4v, wmv)
3. Check that you have sufficient disk space
4. Try processing a shorter video first
5. Check logs for detailed error information

### Intermediate video validation failed

**Error**: "FFprobe could not read the processed video"

**Solution**:
1. This may indicate an OpenCV codec issue
2. Try processing with a different video format
3. Check that you have sufficient disk space
4. Verify the temporary directory is writable

### Configuration validation errors

**Error**: Configuration validation errors displayed on startup

**Solution**:
1. Check the specific error messages
2. Ensure values are within valid ranges (confidence: 0-1, opacity: 0-1, etc.)
3. Verify overlay types are valid (blur, pixelate, emoji, box, image)
4. Check that color values are RGB integers between 0-255

### Out of memory during processing

**Error**: Processing fails or system becomes unresponsive

**Solution**:
1. Process shorter videos
2. Close other applications
3. Increase system RAM
4. Try using a lower resolution video
5. Increase `detect_every_n_frames` to reduce detection frequency

### Emoji not rendering correctly

**Issue**: Emoji appears as a box or doesn't display

**Solution**:
1. The application tries multiple emoji fonts automatically
2. On Windows, ensure "Segoe UI Emoji" is installed
3. On macOS, ensure emoji fonts are available
4. On Linux, install "Noto ColorEmoji" or "Symbola"
5. Consider using a custom image overlay instead

## Limitations

- Face detection may miss partially hidden faces
- Detection boxes are reused between detector frames (no optical-flow tracking)
- Private-region detection is skipped if its model is missing (YOLO) or fails to initialize (NudeNet)
- NudeNet uses a default 320n model; for higher accuracy use the 640m model
- Always review processed videos
- This implementation does not provide a live preview window
- GPU acceleration is not currently implemented (uses CPU only)

## GPU Acceleration (Future Enhancement)

GPU acceleration can significantly speed up detection and processing. To enable GPU acceleration in the future:

1. Install CUDA-compatible versions of dependencies
2. Configure MediaPipe to use GPU
3. Use GPU-enabled OpenCV builds
4. Ensure your NVIDIA GPU has appropriate drivers

This feature is planned for a future release.

## Testing

Run unit tests:

```powershell
python -m pytest tests/
```

Run with coverage:

```powershell
python -m pytest tests/ --cov=autocensor --cov-report=html
```

## Project Structure

```
adult_video_censorship/
├── autocensor/           # Main package
│   ├── __init__.py      # Package initialization
│   ├── constants.py     # Constants and configuration
│   ├── config.py        # Configuration management
│   ├── detectors.py     # Face and private-region detectors
│   ├── overlays.py      # Overlay rendering functions
│   ├── video_processor.py # Video processing with FFmpeg
│   ├── ui.py            # User interface functions
│   ├── gui.py           # Modern CustomTkinter GUI
│   └── main.py          # Main application entry point
├── tests/               # Unit tests
│   ├── __init__.py
│   ├── test_config.py
│   └── test_overlays.py
├── overlays/            # Custom overlay images
├── profiles/            # Configuration profiles
├── models/              # Detection models
├── output/              # Processed videos
├── config.json          # Main configuration
├── requirements.txt     # Python dependencies
├── run.py              # CLI application entry point
├── run_gui.py          # GUI application entry point
└── README.md           # This file
```

## Contributing

Contributions are welcome! Please ensure:

1. Code follows existing style and conventions
2. All functions have type hints and docstrings
3. Unit tests are added for new features
4. Configuration is validated
5. Logging is used instead of print statements

## License

This project is provided as-is for educational and personal use.

## Version History

### v2.1.0 (Current)
- Added modern CustomTkinter GUI with dark theme
- Added video preview with playback controls
- Added real-time configuration editor
- Added detection statistics display
- Added integrated processing button
- Added profile management in GUI
- Added video player with frame scrubbing

### v2.0.0
- Complete modular refactoring
- Added batch processing mode
- Added preview mode
- Added configuration profiles
- Added detection export to JSON
- Added progress bars with tqdm
- Added processing statistics
- Added comprehensive logging
- Added configuration validation
- Added graceful degradation for detector failures
- Added FFmpeg retry logic
- Made overlay paths portable
- Fixed cross-platform emoji support
- Added unit tests
- Pinned all dependencies

### v1.0.0
- Initial release
- Single video processing
- Face detection with MediaPipe
- NudeNet and YOLO private-region detection
- Multiple overlay types
- Configuration via JSON

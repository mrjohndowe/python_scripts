# Overlays Directory

Place custom overlay images here for use with the "image" overlay type.

## Usage

1. Copy your overlay images to this directory
2. In config.json, set the overlay type to "image" and specify the image path:
   ```json
   {
     "type": "image",
     "image": "my_overlay.png"
   }
   ```

## Notes

- Supported formats: PNG, JPG, JPEG, BMP, GIF
- Images will be automatically resized to fit the detection box
- PNG images with transparency are recommended
- You can also use absolute paths if needed

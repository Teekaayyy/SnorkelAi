"""Central configuration for the image processing pipeline."""

from pathlib import Path

# Base directories
APP_DIR = Path("/app")
IMAGES_DIR = APP_DIR / "images"
OUTPUT_DIR = APP_DIR / "output"

# Stage output directories
RESIZED_DIR = OUTPUT_DIR / "resized"
WATERMARKED_DIR = OUTPUT_DIR / "watermarked"

# Final output
CONTACT_SHEET_PATH = OUTPUT_DIR / "contact_sheet.png"

# Resize settings
RESIZE_WIDTH = 800
RESIZE_HEIGHT = 600
RESIZE_DIMENSIONS = f"{RESIZE_HEIGHT}x{RESIZE_WIDTH}"

# Watermark settings
WATERMARK_TEXT = "IMAGES_YES"
WATERMARK_GRAVITY = "Center"
WATERMARK_POINTSIZE = 48
WATERMARK_FILL = "white"
WATERMARK_UNDERCOLOR = "rgba(0,0,0,0.4)"
WATERMARK_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Contact sheet settings
CONTACT_SHEET_COLUMNS = 3
CONTACT_SHEET_GEOMETRY = "+5+5"
CONTACT_SHEET_BACKGROUND = "white"
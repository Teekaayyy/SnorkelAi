#!/bin/bash
# Oracle solution: patch all bugs then run the corrected pipeline.
set -euo pipefail

# Bug 1: settings.py — RESIZE_WIDTH=600, RESIZE_HEIGHT=800 (swapped)
python3 -c "
path = '/app/config/settings.py'
src = open(path).read()
src = src.replace('RESIZE_WIDTH = 600', 'RESIZE_WIDTH = 800')
src = src.replace('RESIZE_HEIGHT = 800', 'RESIZE_HEIGHT = 600')
open(path, 'w').write(src)
print('Bug 1 fixed: RESIZE_WIDTH=800, RESIZE_HEIGHT=600')
"

# Bug 2: settings.py — ZWSP (actual byte) in WATERMARK_TEXT
python3 << 'PYEOF'
path = '/app/config/settings.py'
src = open(path, encoding='utf-8').read()
# Replace the line containing WATERMARK_TEXT with clean version
import re
src = re.sub(
    r'WATERMARK_TEXT = "IMAGES[^"]*YES"',
    'WATERMARK_TEXT = "IMAGES_YES"',
    src
)
open(path, 'w', encoding='utf-8').write(src)
print('Bug 2 fixed: WATERMARK_TEXT cleaned')
PYEOF

# Bug 3: watermark.py — swapped fill/undercolor
python3 -c "
path = '/app/stages/watermark.py'
src = open(path).read()
src = src.replace(
    '\"-fill\", WATERMARK_UNDERCOLOR,\n            \"-undercolor\", WATERMARK_FILL,',
    '\"-fill\", WATERMARK_FILL,\n            \"-undercolor\", WATERMARK_UNDERCOLOR,'
)
open(path, 'w').write(src)
print('Bug 3 fixed: fill/undercolor order restored')
"

# Bug 4: validator.py — h,w swap
python3 -c "
path = '/app/stages/validator.py'
src = open(path).read()
src = src.replace(
    '        h, w = get_dimensions(img)\n        fmt = get_format(img)\n        if (h, w) != expected_dims:',
    '        w, h = get_dimensions(img)\n        fmt = get_format(img)\n        if (w, h) != expected_dims:'
)
src = src.replace(
    '        logger.info(\"Validated resized: %s %s %s\", img.name, (h, w), fmt)',
    '        logger.info(\"Validated resized: %s %s %s\", img.name, (w, h), fmt)'
)
open(path, 'w').write(src)
print('Bug 4 fixed: validator uses w,h not h,w')
"

# Bug 5: pipeline.py — wrong path string in Stage 3 collect_images
python3 << 'PYEOF'
import re
path = '/app/pipeline.py'
src = open(path, encoding='utf-8').read()
# Replace any collect_images call on WATERMARKED_DIR that has extra path component
src = re.sub(
    r'watermarked_images = collect_images\(WATERMARKED_DIR[^)]*\)',
    'watermarked_images = collect_images(WATERMARKED_DIR)',
    src
)
open(path, 'w', encoding='utf-8').write(src)
print('Bug 5 fixed: Stage 3 path in pipeline.py cleaned')
PYEOF

# Clean previous output and run fresh
rm -rf /app/output

cd /app
python pipeline.py
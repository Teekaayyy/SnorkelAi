#!/bin/bash
# Oracle solution: correct implementation of the image processing pipeline.
set -euo pipefail

# Stage 1: Resize all images to exactly 800x600
mkdir -p /app/output/resized
for img in $(ls /app/images/*.png | sort); do
    filename=$(basename "$img")
    convert "$img" -resize 800x600! /app/output/resized/"$filename"
done

# Stage 2: Apply centered IMAGES_YES watermark to each resized image
mkdir -p /app/output/watermarked
for img in $(ls /app/output/resized/*.png | sort); do
    filename=$(basename "$img")
    convert "$img" \
        -gravity Center \
        -pointsize 48 \
        -font /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf \
        -fill "white" \
        -undercolor "rgba(0,0,0,0.4)" \
        -annotate 0 "IMAGES_YES" \
        /app/output/watermarked/"$filename"
done

# Stage 3: Combine watermarked images into a 3-column contact sheet
montage \
    $(ls /app/output/watermarked/*.png | sort | tr '\n' ' ') \
    -tile 3x \
    -geometry +5+5 \
    -background white \
    /app/output/contact_sheet.png
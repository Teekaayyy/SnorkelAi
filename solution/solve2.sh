#!/bin/bash
# Oracle solution for milestone 2: apply IMAGES_YES watermark.
mkdir -p /app/output/watermarked
for img in /app/output/resized/image_1.png /app/output/resized/image_2.png /app/output/resized/image_3.png; do
    filename=$(basename "$img")
    convert "$img" \
        -gravity Center \
        -pointsize 48 \
        -fill "white" \
        -undercolor "rgba(0,0,0,0.3)" \
        -annotate 0 "IMAGES_YES" \
        /app/output/watermarked/"$filename"
done
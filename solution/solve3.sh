#!/bin/bash
# Oracle solution for milestone 3: generate contact sheet.
mkdir -p /app/output
montage \
    /app/output/watermarked/image_1.png \
    /app/output/watermarked/image_2.png \
    /app/output/watermarked/image_3.png \
    -tile 3x1 \
    -geometry +5+5 \
    -background white \
    /app/output/contact_sheet.png
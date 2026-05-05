#!/bin/bash
# Oracle solution for milestone 1: resize images to 800x600.
mkdir -p /app/output/resized
for img in /app/images/image_1.png /app/images/image_2.png /app/images/image_3.png; do
    filename=$(basename "$img")
    convert "$img" -resize 800x600! /app/output/resized/"$filename"
done
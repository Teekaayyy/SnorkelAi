There are 3 images in /app/images/ (image_1.png, image_2.png, image_3.png). Write a python pipeline at /app/pipeline.py that processes them in 3 stages.

First, resize each image to 800x600 and save the results as PNGs to /app/output/resized/. Second, stamp the text "IMAGES_YES" as a watermark on each resized image and write those to /app/output/watermarked/. Third, combine all the watermarked images into a single contact sheet (3 columns) and save it to /app/output/contact_sheet.png.

Use ImageMagick under the hood via subprocess. Output filenames should match the originals.
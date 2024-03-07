from pathlib import Path

import numpy as np
import os
import micasense.imageset as imageset

from micasense import imageutils


# images_path = Path('/Users/michaldolnik/Downloads/_micasense_preprocessing_data/medium_dataset_altum/0000SET')
images_path = Path('/app/data/medium_dataset_altum/0000SET')

Captures = imageset.ImageSet.from_directory(str(images_path))

print(Captures)

generateThumbnails = False
overwrite = True
warp_matrices = None
ground_alt = None

np.float = float

outputPath_for_stacked = os.path.join(images_path, '..', 'stacks')
if not os.path.exists(outputPath_for_stacked):
    os.makedirs(outputPath_for_stacked)

if generateThumbnails:
    thumbnailPath = os.path.join(outputPath_for_stacked, '..', 'thumbnails')
    if not os.path.exists(thumbnailPath):
        os.makedirs(thumbnailPath)


for Capture in Captures.captures:
    image_name_blue = Capture.images[0].meta.get_item("File:FileName")
    image_name = image_name_blue[0:-6]  # remove '_1.tif'
    outputFilename = image_name + '.tif'
    full_outputPath_for_stacked = os.path.join(outputPath_for_stacked, outputFilename)
    if (not os.path.exists(full_outputPath_for_stacked)) or overwrite:
        if len(Capture.images) == len(Captures.captures[0].images):
            irradiance = Capture.dls_irradiance()

            Capture.create_aligned_capture(irradiance_list=irradiance,
                                           warp_matrices=warp_matrices)  # convert to reflectance

            Capture.save_capture_as_stack(full_outputPath_for_stacked)

            imageutils.write_exif_to_stack(Capture, full_outputPath_for_stacked)

    Capture.clear_image_data()

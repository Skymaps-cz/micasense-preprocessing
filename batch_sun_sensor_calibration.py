

import numpy as np
import micasense.dls as dls
import os, glob
import micasense.capture as capture
import math
import matplotlib.pyplot as plt
import micasense.imageset as imageset
import pandas as pd
import subprocess


images_path = os.path.expanduser(os.path.join('~','Downloads', '_micasense_preprocessing_data', '4347', '0002SET'))

imlist = imageset.ImageSet.from_directory(images_path)

dls_coef = np.array([1, 1, 1, 1, 1, 1]) 
generateThumbnails = True
overwrite = False
warp_matrices = None
ground_alt = None

np.float = float


outputPath_for_stacked = os.path.join(images_path,'..','stacks')
if not os.path.exists(outputPath_for_stacked):
    os.makedirs(outputPath_for_stacked)

if generateThumbnails:
    thumbnailPath = os.path.join(outputPath_for_stacked, '..', 'thumbnails')
    if not os.path.exists(thumbnailPath):
        os.makedirs(thumbnailPath)

for i,cap in enumerate(imlist.captures):

    if ground_alt:
            _,_, alt_above_see = cap.location()
            flight_alt = alt_above_see - ground_alt

    image_name_blue = cap.images[0].meta.get_item("File:FileName")
    image_name = image_name_blue[0:-6] # remove '_1.tif'
    outputFilename = image_name+'.tif'  
        
    full_outputPath_for_stacked = os.path.join(outputPath_for_stacked, outputFilename)

    if (not os.path.exists(full_outputPath_for_stacked)) or overwrite:
        if(len(cap.images) == len(imlist.captures[0].images)):

            print(cap.dls_irradiance())

            irradiance = cap.dls_irradiance()
            
            cap.create_aligned_capture(irradiance_list=irradiance, warp_matrices = warp_matrices) # convert to reflectance
            
            cap.save_capture_as_stack(full_outputPath_for_stacked)
            
            if generateThumbnails:
                thumbnailFilename = image_name + '.jpg'
                fullThumbnailPath= os.path.join(thumbnailPath, thumbnailFilename)
                cap.save_capture_as_rgb(fullThumbnailPath)
    cap.clear_image_data()




def copy_exif_data_to_stack(source_dir, stack_dir):
    source_tiffs = glob.glob(os.path.join(source_dir,'**/*_1.tif'))

    stacked_tiffs = glob.glob(os.path.join(stack_dir,'*.tif'))
    print(stacked_tiffs)
    
    # Ensure the source file exists
    if not os.path.isdir(source_dir):
        raise FileNotFoundError(f"Source file not found: {source_dir}")

    # Ensure the target file exists
    if not os.path.isdir(stack_dir):
        raise FileNotFoundError(f"Target file not found: {stack_dir}")
    
    for stacked_tiff in stacked_tiffs:
        stacked_filename = stacked_tiff.split('/')[-1].split('.')[0]
        print('stacked_filename', stacked_filename)
        source_tiff = [tiff for tiff in source_tiffs if stacked_filename in tiff][0]
        print('source_tiff', source_tiff)
        
        # Command to copy EXIF data from source to target
        command = f"exiftool -config exiftool.config -overwrite_original -TagsFromFile {source_tiff} -all:all {stacked_tiff}"

        # Execute the command
        subprocess.run(command, shell=True, check=True)


# copy_exif_data_to_stack(images_path, os.path.expanduser(os.path.join('~','Downloads', '_micasense_preprocessing_data', 'Pix4D_test_Average-DNG_ALtumPT_cw-padderok_230910','stacks')))
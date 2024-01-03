import os
import cv2
import glob
import matplotlib.pyplot as plt
import micasense.utils as msutils
from micasense.image import Image
from micasense.panel import Panel
import micasense.metadata as metadata
import exiftool
import rasterio
import subprocess
import numpy as np

np.float = float

exiftoolPath = None
if os.name == 'nt':
    exiftoolPath = os.environ.get('exiftoolpath')

camera = 'altum'

root_dir_path = os.path.expanduser(os.path.join('/app','data', 'MS','0000SET'))
images_path = os.path.expanduser(os.path.join('/app','data', 'MS','0000SET'))
images = glob.glob(os.path.join(images_path,'*/IMG_*.tif'))
images = [file for file in images if not file.endswith('_6.tif')]


def copy_exif_data(source_file, target_file):
    # Ensure the source file exists
    if not os.path.isfile(source_file):
        raise FileNotFoundError(f"Source file not found: {source_file}")

    # Ensure the target file exists
    if not os.path.isfile(target_file):
        raise FileNotFoundError(f"Target file not found: {target_file}")

    # Command to copy EXIF data from source to target
    command = f"exiftool -config exiftool.config -overwrite_original -TagsFromFile {source_file} -all:all {target_file}"

    # Execute the command
    subprocess.run(command, shell=True, check=True)



def panel_detection(root_dir_path):
    dirs = sorted(os.listdir(root_dir_path))
    dirs.insert(0, dirs.pop())

    panel_calibration = {}
    for dir in dirs:
        path = os.path.join(root_dir_path, dir)
        path_images = glob.glob(os.path.join(path,'IMG_*.tif'))

        for image in path_images:
            meta = metadata.Metadata(image, exiftoolPath=exiftoolPath)
            img = Image(image)
            panel = Panel(img)
            
            if panel.panel_detected():
                band_name = meta.get_item('XMP:BandName')
                mean, std, count, saturated_count = panel.raw()
                panel_reflectance = panel.reflectance_from_panel_serial()
                panel_calibration[band_name] = panel_reflectance
                panel_calibration_band_number = len(panel_calibration.keys())
                if panel_calibration_band_number == 5 and camera == 'altum':
                    return panel_calibration, mean
    

# panel_detection(root_dir_path)

panel_calibration, mean_radiance = panel_detection(root_dir_path)


def radiance_to_reflectance(images, panelCalibration, meanRadiance):

    for image_name in images:
        imageRaw=plt.imread(image_name)
        meta = metadata.Metadata(image_name, exiftoolPath=exiftoolPath)
        radianceImage, _, _, _ = msutils.raw_image_to_radiance(meta, imageRaw)

        bandName = meta.get_item('XMP:BandName')
        panelReflectance = panelCalibration[bandName]
        radianceToReflectance = panelReflectance / meanRadiance
        reflectanceImage = radianceImage * radianceToReflectance

        # correct for lens distortions to make straight lines straight
        undistortedReflectance = msutils.correct_lens_distortion(meta, reflectanceImage)
        img_file_name = image_name.split('/')[-1]
        sub_folder = image_name.split('/')[-2]

        if os.path.exists(os.path.expanduser(os.path.join('/app','data', '_radiance_to_reflectance', sub_folder))) == False:
            os.mkdir(os.path.expanduser(os.path.join('/app', 'data', '_radiance_to_reflectance', sub_folder)))
        path_to_save = os.path.expanduser(os.path.join('/app', 'data', '_radiance_to_reflectance', sub_folder))

        img_undistorted_reflectance = rasterio.open(path_to_save + '/' + img_file_name, 'w', driver='GTiff',
                                height=undistortedReflectance.shape[0], width=undistortedReflectance.shape[1],
                                count=1, dtype=str(undistortedReflectance.dtype),
                                )
        img_undistorted_reflectance.write(undistortedReflectance, 1)
        img_undistorted_reflectance.close()
        copy_exif_data(image_name, path_to_save + '/' + img_file_name)




radiance_to_reflectance(images, panel_calibration, mean_radiance)
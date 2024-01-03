

import numpy as np
import micasense.dls as dls
import os, glob
import micasense.capture as capture
import math
import matplotlib.pyplot as plt
import micasense.imageset as imageset
import pandas as pd


images_path = os.path.expanduser(os.path.join('~','Downloads','medium_dataset_altum', 'MS','0000SET', '004'))

imlist = imageset.ImageSet.from_directory(images_path)

dls_coef = np.array([1, 1, 1, 1, 1, 1]) 
generateThumbnails = True
overwrite = False
warp_matrices = None
ground_alt = None


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

            irradiance = dls_coef * cap.dls_irradiance()
            
            cap.create_aligned_capture(irradiance_list=irradiance, warp_matrices = warp_matrices) # convert to reflectance
            
            cap.save_capture_as_stack(full_outputPath_for_stacked)
            
            if generateThumbnails:
                thumbnailFilename = image_name + '.jpg'
                fullThumbnailPath= os.path.join(thumbnailPath, thumbnailFilename)
                cap.save_capture_as_rgb(fullThumbnailPath)
    cap.clear_image_data()

    # save_meta = saveMetadata(cap, outputPath_for_stacked)



# images_path = os.path.expanduser(os.path.join('~','Downloads','medium_dataset_altum', 'MS','0000SET', '004'))
# image_names = glob.glob(os.path.join(images_path,'IMG_*.tif'))
# print(len(image_names))
# cap = capture.Capture.from_filelist(image_names)

# print(cap)

# # Define DLS sensor orientation vector relative to dls pose frame
# dls_orientation_vector = np.array([0,0,-1])
# # compute sun orientation and sun-sensor angles
# (
#     sun_vector_ned,    # Solar vector in North-East-Down coordinates
#     sensor_vector_ned, # DLS vector in North-East-Down coordinates
#     sun_sensor_angle,  # Angle between DLS vector and sun vector
#     solar_elevation,   # Elevation of the sun above the horizon
#     solar_azimuth,     # Azimuth (heading) of the sun
# ) = dls.compute_sun_angle(cap.location(),
#                       cap.dls_pose(),
#                       cap.utc_time(),
#                       dls_orientation_vector)

# # Since the diffuser reflects more light at shallow angles than at steep angles,
# # we compute a correction for this
# fresnel_correction = dls.fresnel(sun_sensor_angle)



# # Now we can correct the raw DLS readings and compute the irradiance on level ground
# dls_irradiances = []
# center_wavelengths = []
# for img in cap.images:
#     dir_dif_ratio = 6.0
#     percent_diffuse = 1.0/dir_dif_ratio
#     # measured Irradiance / fresnelCorrection
#     sensor_irradiance = img.spectral_irradiance / fresnel_correction
#     untilted_direct_irr = sensor_irradiance / (percent_diffuse + np.cos(sun_sensor_angle))
#     # compute irradiance on the ground using the solar altitude angle
#     dls_irr = untilted_direct_irr * (percent_diffuse + np.sin(solar_elevation))
#     dls_irradiances.append(dls_irr)
#     center_wavelengths.append(img.center_wavelength)


# plt.scatter(center_wavelengths,dls_irradiances)
# plt.xlabel('Wavelength (nm)')
# plt.ylabel('Irradiance ($W/m^2/nm$)')
# plt.show()

# cap.plot_undistorted_reflectance(dls_irradiances)

# panel_reflectance_by_band = [0.49] * len(cap.eo_band_names()) # This panel has an average of 49% reflectance for each EO band

# panel_radiances = np.array(cap.panel_radiance())
# irr_from_panel = math.pi * panel_radiances / panel_reflectance_by_band
# dls_correction = irr_from_panel/dls_irradiances
# cap.plot_undistorted_reflectance(dls_irradiances*dls_correction)

# plt.scatter(cap.center_wavelengths(), cap.panel_reflectance())
# plt.title("Panel Reflectances")
# plt.xlabel("Wavelength (nm)")
# plt.ylabel("Reflectance")
# plt.show()
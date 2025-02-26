import rasterio
import pandas as pd
import numpy as np
import os
import logging
import datetime
from pathlib import Path
from osgeo import gdal

def read_band(input_raster, n_band=1, no_data=-9999, rnd=None):
    '''converts a raster file to xyz'''
    # GetRasterData - Getting geotransform and data
    src_raster = gdal.Open(input_raster)
    raster_bnd = src_raster.GetRasterBand(n_band)

    raster_values = raster_bnd.ReadAsArray()
    gtr = src_raster.GetGeoTransform()

    src_raster = None

    # Get XYZ Data 
    if not no_data:
        no_data = np.nan

    y, x = np.where(raster_values != no_data)
    data_vals = np.extract(raster_values != no_data, raster_values)

    # geotrCoords - Getting geotransformed coordinates
    gtr_x = gtr[0] + (x + 0.5) * gtr[1] + (y + 0.5) * gtr[2]
    gtr_y = gtr[3] + (x + 0.5) * gtr[4] + (y + 0.5) * gtr[5]

    # Build XYZ Data
    data_dict = {
        "longitude": gtr_x,
        "latitude": gtr_y,
        'z': data_vals
    }

    df = pd.DataFrame(data_dict)

    if rnd:
        rnd_x, rnd_y, rnd_z = rnd
        rnd_df = df.round({'longitude': rnd_x, 'latitude': rnd_y, 'z': rnd_z})
        return rnd_df

    return df


def read_multiband(input_raster, dropna=False):
    with rasterio.open(input_raster) as src:
        band_count = src.count
        src_bands = [src.descriptions[i] for i in range(band_count)]

    data_frames = [read_band(input_raster, n_band=i) for i in range(1, band_count+1)]
    gps_coords = data_frames[0][["longitude", "latitude"]]

    bands = pd.concat([df["z"] for df in data_frames], axis=1)
    bands.columns = src_bands

    df = pd.concat([gps_coords, bands], axis=1)

    if not dropna:
        return df
    else:
        df = df.dropna()
        return df.reset_index(drop=True)
    
import matplotlib.pyplot as plt
from rasterio.enums import Resampling
# https://rasterio.readthedocs.io/en/latest/api/rasterio.enums.html#rasterio.enums.Resampling


def plot_raster_bands(filename, band1=0, band2=1):
    with rasterio.open(filename) as src:
        band_count = src.count
        bands = src.read()

         # Create a figure with two subplots for the bands 
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        parameters = [src.descriptions[i] for i in range(band_count)]
        print("Bands:", parameters)
        # Display MODIS bands 
        im1 = ax1.imshow(bands[band1], cmap='viridis') 
        ax1.set_title(parameters[band1])

        # Display ERA5 bands
        im2 = ax2.imshow(bands[band2], cmap='viridis') 
        ax2.set_title(parameters[band2])


def merge_rasters(filename1, filename2, output_path="output.tif", shape=''):
    ''' 
    Merge two raster files. 
    Parameters: 
        - filename1: file name of the 1st raster file to be merged. This will be the default shape of the merged output raster
        - filename2: file name of the 2nd raster file to be merged
        - output_path: str, file name for output raster file 
        - shape: tuple of length and width custom output shape '''

    print("Merging rasters...")
    # Load the two images 
    with rasterio.open(filename1) as src1, rasterio.open(filename2) as src2:

        if not shape:
            shape=src1.shape

        src1_count = src1.count
        src2_count = src2.count

        src1_bands = [src1.descriptions[i] for i in range(src1_count)]
        src2_bands = [src2.descriptions[i] for i in range(src2_count)]

        
        # Reproject the second image to match the CRS of the first image
        src2_read = src2.read(
            out_shape=shape,
            resampling=Resampling.nearest
        )
        
        # Register GDAL format drivers and configuration options with a context manager.
        with rasterio.Env():

            # Write an array as a raster band to a new 8-bit file. For
            # the new file's profile, we start with the profile of the source
            profile = src1.profile

            # And then change the band count to 1, set the
            # dtype to uint8, and specify LZW compression.
            profile.update(
                dtype=src1.dtypes[0],
                width=shape[1],
                height=shape[0],
                count=src1_count+src2_count)

            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(src1.read(), [i for i in range(1, src1_count+1)])
                dst.write(src2_read, [i for i in range(src1_count+1, src1_count+src2_count+1)]) 

                dst.crs = src1.crs
                dst.transform = src1.transform
                dst.descriptions = src1_bands + src2_bands

        # At the end of the ``with rasterio.Env()`` block, context
        # manager exits and all drivers are de-registered.

    return shape


def clean_raster_dataframe(df):
    df_clean = df.iloc[:,2:].dropna(axis = 0, 
                    how = 'all')
    df_clean.shape
    df_clean.loc[~(df_clean == 0.0).all(axis = 1)]
    df_clean = df_clean.fillna(0)
    df_clean_idx = df_clean.index

    return df_clean, df_clean_idx


def get_logger(
        script_name,
        log_directory,
        log_format='%(asctime)s;%(name)s;%(levelname)s;%(message)s',
        log_level=logging.DEBUG):

    logger = logging.getLogger(script_name)
    logger.setLevel(log_level)
    Path(str(log_directory)).mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(os.path.join(
        log_directory,
        datetime.datetime.strftime(
            datetime.datetime.now(),
            f"%Y-%m-%dT%H%M%S.{script_name}.log")))

    formatter = logging.Formatter(log_format)
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    return logger


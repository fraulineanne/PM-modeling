import os
import click
import time
import ee
from datetime import date, timedelta
from google.cloud import storage
import os
from utils import read_multiband
from utils import merge_rasters
from utils import clean_raster_dataframe
import joblib
import numpy as np
import matplotlib.pyplot as plt
from skimage import exposure
from download_satellite import download_modis, download_era5

today = date.today() - timedelta(days=1)
yesterday = str(today - timedelta(days=1))

def predict(
    project, bucket_name, from_date, to_date, 
    service_account, service_file, saved_model
):

    credentials = ee.ServiceAccountCredentials(service_account, service_file)

    storage_client = storage.Client(project=project, credentials=credentials) # create client object with gcp project
    bucket = storage_client.bucket(bucket_name)

    # Create new directory to a temporary location
    directory = 'tmp'
    os.makedirs(directory, exist_ok = True)

    _date = ''.join(filter(str.isalnum, from_date)) 

    # Check if satellite image in GCS exists
    modis_tif = f"MODIS_{_date}.tif"
    modis_filename = f'{directory}/{modis_tif}'
    modis = bucket.blob(modis_tif)
    if modis.exists(): # if file exists, download the file locally
        # modis.download_to_filename(modis_filename)
        print(f"Downloaded {modis_tif}")
    else: # else, download the file from Earth Engine
        print(f"File {modis_tif} does not exist in the bucket.")
        download_modis(credentials, from_date=from_date, to_date=to_date)

    era5_tif = f"ERA5_{_date}.tif"
    era5_filename = f'{directory}/{era5_tif}'
    era5 = bucket.blob(era5_tif)
    if era5.exists():
        # era5.download_to_filename(era5_filename)
        print(f"Downloaded {era5_tif}")
    else:
        print(f"File {era5_tif} does not exist in the bucket.")
        download_era5(credentials, from_date=from_date, to_date=to_date)
    
    # download all satellite images from input date
    # while not os.path.exists(modis_filename) or not os.path.exists(era5_filename):
    #     print(f"Waiting for satellite data to be downloaded...")
    #     time.sleep(3)
        
    shape = merge_rasters(f'/vsigs/{bucket_name}/{modis_tif}', F'/vsigs/{bucket_name}/{era5_tif}', output_path=f'{directory}/output.tif')
    df = read_multiband(f'{directory}/output.tif')
    df_clean, df_clean_idx = clean_raster_dataframe(df)

    model_tuned = joblib.load(saved_model)
    prediction = model_tuned.predict(df_clean) # predict using tuned model
    df_plot = df
    df_plot.loc[df_clean_idx, 'prediction'] = prediction

    img_eq = exposure.equalize_hist(prediction)

    df_plot.loc[df_clean_idx, 'prediction_eq'] = img_eq
    fig, ax = plt.subplots()
    df_as_array = np.array(df_plot['prediction_eq']).reshape(shape[0],shape[1])

    cax = ax.imshow(df_as_array, 
                    cmap = 'Spectral_r')
    plt.axis('off')
    plt.savefig('output/output.png', bbox_inches='tight', pad_inches=0) 

    # Upload the output image to GCS
    output_blob = bucket.blob('output/output.png')
    output_blob.upload_from_filename('output/output.png')
    print(f"Uploaded output/output.png to {bucket_name}")

    url = "https://storage.googleapis.com/earth-engine-storage-care/output/output.png"
    return url
    # plt.show()

    # # Delete the temporary directory
    # shutil.rmtree(directory)

if __name__ == '__main__':
    predict()
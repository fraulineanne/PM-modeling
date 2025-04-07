import ee
import geetools

def download_modis(from_date, to_date, credentials, bucket):

    ee.Initialize(credentials)

    philippines = ee.Geometry.Polygon(
        [[[116.71687839753203, 18.744929081691417],
            [116.71687839753203, 5.019622515938524],
            [126.91219089753203, 5.019622515938524],
            [126.91219089753203, 18.744929081691417]]], None, False)

    _from = from_date.split("-")
    _to = to_date.split("-")

    collection = ee.ImageCollection(
        'MODIS/061/MCD19A2_GRANULES').filter(
        ee.Filter.stringContains('system:index', 'h29v07')).select(
            'Optical_Depth_047', 
            'Optical_Depth_055'
            ).filterBounds(philippines)

    startDate = ee.Date.fromYMD(int(_from[0]), int(_from[1]), int(_from[2]))
    endDate = ee.Date.fromYMD(int(_to[0]), int(_to[1]), int(_to[2]))
    nDays = ee.Number(endDate.difference(startDate, 'day')).round()
    daysList = ee.List.sequence(0, nDays)

    def getDailyAve(n):
        ini = startDate.advance(n, 'day')
        end = ini.advance(1, 'day')
        datared = collection.filterDate(ini, end).mean()
        day = ini.get("day")
        month = ini.get("month")
        year = ini.get("year")

        day = ee.String(ini.get("day"))
        month = ee.String(ini.get("month"))
        year = ee.String(ini.get("year"))
        
        sysIndexinfo = ee.String(f"MODIS_{from_date}_{to_date}")
        return datared.set('year', year).set('month', month).set('day', day).set('system:time_start', ini.millis()).set("system:index", sysIndexinfo)
    
    dailyAve_Listversion = daysList.map(getDailyAve)
    modis = ee.ImageCollection(dailyAve_Listversion)

    if modis.size().getInfo() == 0:
        print("No MODIS data found.")
    else:
        extra = dict(sat="MODIS")
        modis_task = geetools.batch.Export.imagecollection.toCloudStorage(
            collection=modis,
            bucket = bucket,
            scale =  1000,
            region = philippines,
            namePattern='{sat}_{system_date}',
            datePattern='yMMdd',
            extra=extra,
            verbose=True
        )
    
def download_era5(from_date, to_date, credentials, bucket):
    
    ee.Initialize(credentials)

    philippines = ee.Geometry.Polygon(
        [[[116.71687839753203, 18.744929081691417],
            [116.71687839753203, 5.019622515938524],
            [126.91219089753203, 5.019622515938524],
            [126.91219089753203, 18.744929081691417]]], None, False)

    era5 = ee.ImageCollection(
    'ECMWF/ERA5_LAND/DAILY_AGGR').select(
        'u_component_of_wind_10m',
        'v_component_of_wind_10m',
        'temperature_2m',
        'temperature_2m_min',
        'temperature_2m_max',
        'total_precipitation_sum',
        'surface_pressure'
        ).filterBounds(philippines).filterDate(
            from_date, to_date)

    if era5.size().getInfo() == 0:
        print("No ERA5 data found.")
    else:
        extra = dict(sat="ERA5")
        era5_task = geetools.batch.Export.imagecollection.toCloudStorage(
            collection=era5,
            bucket=bucket,
            region=philippines,
            scale=31000,
            namePattern='{sat}_{system_date}',
            datePattern='yMMdd',
            extra=extra,
            verbose=True,
    )
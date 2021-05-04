"""
File Format Properties
"""

def vector_formats():
    return [
        '.shp', '.gml', '.json', '.geojson', '.kml',
        '.osm', '.pbf', '.dbf', '.vct', '.nc', '.vrt',
        '.sqlite', '.gdb'
    ]


def raster_formats():
    return [
        '.tiff', '.tif', '.img', '.nc', 'ecw', '.jpg', '.png', '.vrt', '.jp2',
        '.asc'
    ]


def check_isRaster(_file):
    from pycode.oss import fprop

    rst_lst = raster_formats()
    
    file_ext = fprop(_file, 'ff')
    
    if file_ext not in rst_lst:
        return None
    else:
        return True


def check_isShp(_file):
    from pycode.oss import fprop
    
    lst = vector_formats()
    
    file_ext = fprop(_file, 'ff')
    
    if file_ext not in lst:
        return None
    else:
        return True



"""
Deal with Geospatial Files
"""

import os

def drv_name(_file):
    """
    Return the driver for a given file format
    """
    
    drv = {
        # Vector files
        '.gml'    : 'GML',
        '.shp'    : 'ESRI Shapefile',
        '.json'   : 'GeoJSON',
        '.kml'    : 'KML',
        '.osm'    : 'OSM',
        '.dbf'    : 'ESRI Shapefile',
        '.vct'    : 'Idrisi',
        '.nc'     : 'netCDF',
        '.vrt'    : 'VRT',
        '.mem'    : 'MEMORY',
        '.sqlite' : 'SQLite',
        '.gdb'    : 'FileGDB',
        # Raster files
        '.tif'    : 'GTiff',
        '.ecw'    : 'ECW',
        '.mpr'    : 'ILWIS',
        '.mpl'    : 'ILWIS',
        '.jpg'    : 'JPEG',
        '.png'    : 'PNG',
        '.asc'    : 'AAIGrid',
        '.img'    : 'HFA'
    }
    return str(drv[os.path.splitext(_file)[1]])


def grs_rst_drv():
    return {
        '.tif': 'GTiff',
        '.img': 'HFA'
    }


def list_esri_shp(datafolder):
    """
    List ESRI Shapefiles in Folder
    """

    files = []
    for (d, _d, f) in os.walk(datafolder):
        files.extend(f)
        break

    return [f for f in files if f.split('.')[-1] == 'shp']


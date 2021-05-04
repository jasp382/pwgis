"""
Get Raster properties
"""

def rst_ext(rst):
    """
    Return a array with the extent of one raster dataset
    
    array order = Xmin (left), XMax (right), YMin (bottom), YMax (top)
    """
    
    from osgeo import gdal
        
    img = gdal.Open(rst)
        
    lnhs = int(img.RasterYSize)
    cols = int(img.RasterXSize)
        
    left, cellx, z, top, c, celly = img.GetGeoTransform()
        
    right  = left + (cols * cellx)
    bottom = top  - (lnhs * abs(celly))
        
    extent = [left, right, bottom, top]
    
    return extent


def get_cellsize(rst):
    """
    Return cellsize of one Raster Datasets
    """
    
    from osgeo import gdal

    img = gdal.Open(rst)

    (tlx, x, xr, tly, yr, y) = img.GetGeoTransform()
        
    return x


def rst_shape(rst):
    """
    Return number of lines and columns in a raster
    """
    
    from pycode import obj_to_lst
    from pycode.rd import rst_to_array
    
    rst    = obj_to_lst(rst)
    shapes = {}
        
    for r in rst:
        array     = rst_to_array(r)
        lnh, cols = array.shape
            
        shapes[r] = [lnh, cols]
            
        del array
    
    return shapes if len(rst) > 1 else shapes[rst[0]]


def get_nd(img):
    """
    Return NoData Value
    """

    band = img.GetRasterBand(1)

    return band.GetNoDataValue()


def frequencies(r, excludeNoData=True):
    """
    Return frequencies table
    """
    
    import numpy as np
    from osgeo import gdal
    
    if type(r).__name__ == 'str':
        img = gdal.Open(r)
        arr = img.ReadAsArray()
    elif type(r).__name__ == 'Dataset':
        img = r
        arr = img.ReadAsArray()
    else:
        img = None
        arr = r
    
    unique = list(np.unique(arr))
    
    one_arr = arr.reshape(arr.shape[0] * arr.shape[1])
    
    freq    = np.bincount(one_arr)
    freq    = freq[freq != 0]
    
    if excludeNoData:
        if type(r).__name__ == 'str' or type(r).__name__ == 'Dataset':
            ndval = get_nd(img)
            return {
                unique[i] : freq[i] for i in range(len(unique)) \
                    if unique[i] != ndval
            }
        
        else:
            return {unique[i] : freq[i] for i in range(len(unique))}
    else:
        return {unique[i] : freq[i] for i in range(len(unique))}


"""
Raster Statistics
"""

def rst_stats(rst, bnd=None):
    """
    Get Raster Statistics
    
    The output will be a dict with the following keys:
    * Min - Minimum
    * Max - Maximum
    * Mean - Mean value
    * StdDev - Standard Deviation
    """

    from osgeo import gdal
        
    r = gdal.Open(rst)
        
    bnd = r.GetRasterBand(1 if not bnd else bnd)
    stats = bnd.GetStatistics(True, True)
        
    dicStats = {
        'MIN' : stats[0], 'MAX' : stats[1], 'MEAN' : stats[2],
        "STDEV" : stats[3]
    }
    
    return dicStats


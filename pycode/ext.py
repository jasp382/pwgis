"""
Extent to data files
"""

def ext_to_rst(topLeft, btRight, outRst,
               cellsize=None, epsg=None, outEpsg=None,
               invalidResultAsNull=None, rstvalue=None):
    """
    Extent to Raster
    """
    
    import numpy
    from osgeo           import gdal
    from pycode.geofiles import drv_name
    
    left, top     = topLeft
    right, bottom = btRight
    
    cellsize = 10 if not cellsize else cellsize
    
    if outEpsg and epsg and outEpsg != epsg:
        from pycode.gobj import new_pnt, create_polygon
        from pycode.prj import prj_ogrgeom
        
        extGeom = prj_ogrgeom(create_polygon([
            new_pnt(left, top), new_pnt(right, top),
            new_pnt(right, bottom), new_pnt(left, bottom), new_pnt(left, top)
        ]), epsg, outEpsg)

        epsg = outEpsg
        
        left, right, bottom, top = extGeom.GetEnvelope()
    
    # Get row and cols number
    rows = (float(top) - float(bottom)) / cellsize
    cols = (float(right) - float(left)) / cellsize
    
    rows = int(rows) if rows == int(rows) else int(rows) + 1
    cols = int(cols) if cols == int(cols) else int(cols) + 1
    
    if not invalidResultAsNull:
        if not rstvalue:
            NEW_RST_ARRAY = numpy.zeros((rows, cols))
        
        else:
            NEW_RST_ARRAY = numpy.full((rows, cols), rstvalue)
    else:
        try:
            if not rstvalue:
                NEW_RST_ARRAY = numpy.zeros((rows, cols))
            
            else:
                NEW_RST_ARRAY = numpy.full((rows, cols), rstvalue)
        except:
            return None
    
    # Create new Raster
    img = gdal.GetDriverByName(drv_name(outRst)).Create(
        outRst, cols, rows, 1, gdal.GDT_Byte
    )
    
    img.SetGeoTransform((left, cellsize, 0, top, 0, -cellsize))
    
    band = img.GetRasterBand(1)
    
    band.WriteArray(NEW_RST_ARRAY)
    
    if epsg:
        from osgeo import osr
        
        rstSrs = osr.SpatialReference()
        rstSrs.ImportFromEPSG(epsg)
        img.SetProjection(rstSrs.ExportToWkt())
    
    band.FlushCache()
    
    return outRst


def rstext_to_rst(inrst, outrst, cellsize=None, epsg=None, rstval=None):
    """
    Raster Extent to Raster
    """

    from pycode.prop.rst import rst_ext, get_cellsize

    # Get Raster Extent
    left, right, bottom, top = rst_ext(inrst)

    # GET EPSG
    if not epsg:
        from pycode.prop.prj import get_rst_epsg

        epsg = get_rst_epsg(inrst)
    
    # Create raster
    ext_to_rst(
        (left, top), (right, bottom), outrst,
        cellsize=get_cellsize(inrst) if not cellsize else cellsize,
        epsg=epsg, rstvalue=rstval
    )

    return outrst
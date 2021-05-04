"""
Spatial Reference Systems Properties
"""

from osgeo import osr

def get_trans_param(in_epsg, out_epsg, export_all=None):
    """
    Return transformation parameters for two Spatial Reference Systems
    """
    
    i = osr.SpatialReference()
    i.ImportFromEPSG(in_epsg)
    o = osr.SpatialReference()
    o.ImportFromEPSG(out_epsg)
    t = osr.CoordinateTransformation(i, o)
    if not export_all:
        return t
    else:
        return {'input': i, 'output': o, 'transform': t}


"""
Raster Spatial Reference Systems
"""

def rst_epsg(img, isproj=None):
    """
    Return Raster EPSG
    """

    from osgeo import osr

    proj = osr.SpatialReference(wkt=img.GetProjection())

    if not proj:
        raise ValueError(
            'img obj has not Spatial Reference assigned!'
        )
    
    epsg = int(str(proj.GetAttrValue(str('AUTHORITY'), 1)))

    if not isproj:
        return epsg
    
    else:
        if proj.IsProjected:
            mod_proj = proj.GetAttrValue(str('projcs'))

            if not mod_proj:
                return epsg, None
            
            else:
                return epsg, True
        else:
            return epsg, None


def get_rst_epsg(rst, returnIsProj=None):
    """
    Return the EPSG Code of the Spatial Reference System of a Raster
    """
    
    import os
    from osgeo import gdal
    
    if not os.path.exists(rst):
        raise ValueError((
            "{} does not exist! Please give a valid "
            "path to a raster file"
        ).format(rst))
    
    d    = gdal.Open(rst)
    
    if not returnIsProj:
        epsg = rst_epsg(d, isproj=None)

        return epsg
    else:
        epsg, isproj = rst_epsg(d, isproj=True)

        return epsg, isproj


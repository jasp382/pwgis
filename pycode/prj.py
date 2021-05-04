"""
Manage projections
"""

def get_shp_sref(shp):
    """
    Get Spatial Reference Object from Feature Class/Lyr
    """
    
    from osgeo           import ogr
    from pycode.geofiles import drv_name
    
    if type(shp) == ogr.Layer:
        lyr = shp
        
        c = 0
    
    else:
        data = ogr.GetDriverByName(
            drv_name(shp)).Open(shp)
        
        lyr = data.GetLayer()
        c = 1
    
    spref = lyr.GetSpatialRef()
    
    if c:
        del lyr
        data.Destroy()
    
    return spref


def epsg_to_wkt(epsg):
    from osgeo import osr

    s = osr.SpatialReference()
    s.ImportFromEPSG(epsg)
    
    return s.ExportToWkt()


def prj_ogrgeom(geom, in_epsg, out_epsg, api='ogr'):
    """
    Project OGR Geometry

    API Options:
    * ogr;
    * shapely or shply;
    """

    from osgeo import ogr
    

    if api == 'ogr':
        from pycode.prop.prj import get_trans_param

        newg = ogr.CreateGeometryFromWkt(geom.ExportToWkt())

        newg.Transform(get_trans_param(in_epsg, out_epsg))
    
    elif api == 'shapely' or api == 'shply':
        import pyproj
        from shapely.ops import transform
        from shapely.wkt import loads

        shpgeom = loads(geom.ExportToWkt())

        srs_in = pyproj.Proj('epsg:' + str(in_epsg))
        srs_ou = pyproj.Proj('epsg:' + str(out_epsg))

        proj = pyproj.Transformer.from_proj(
            srs_in, srs_ou, always_xy=True
        ).transform

        newg = transform(proj, shpgeom)
        newg = ogr.CreateGeometryFromWkt(newg.wkt)
    
    else:
        raise ValueError('API {} is not available'.format(api))

    return newg


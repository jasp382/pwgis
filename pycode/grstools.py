"""
GRASS GIS tools
"""

def rst_to_grs(rst, grsRst, lmtExt=None, as_cmd=None):
    """
    Raster to GRASS GIS Raster
    """
    
    if not as_cmd:
        from grass.pygrass.modules import Module
        
        __flag = 'o' if not lmtExt else 'or'
        
        m = Module(
            "r.in.gdal", input=rst, output=grsRst, flags='o',
            overwrite=True, run_=False, quiet=True,
        )
        
        m()
    
    else:
        from pycode.oss import execmd
        
        rcmd = execmd((
            "r.in.gdal input={} output={} -o{} --overwrite "
            "--quiet"
        ).format(rst, grsRst, "" if not lmtExt else " -r"))
    
    return grsRst


def grs_viewshed(dem, obs_pnt, out_rst, max_dist=None, obs_elv=None):
    """
    Compute viewshed
    """
    
    from grass.pygrass.modules import Module
    
    vshd = Module(
        "r.viewshed", input=dem, output=out_rst,
        coordinates=obs_pnt,
        flags="b", overwrite=True, run_=False, quiet=True,
        max_distance=-1 if not max_dist else max_dist,
        observer_elevation=1.75 if not obs_elv else obs_elv
    )
    
    vshd()
    
    return out_rst


def rstcalc(expression, output, api='pygrass'):
    """
    Basic Raster Calculator
    """
    
    if api == 'pygrass':
        from grass.pygrass.modules import Module
        
        rc = Module(
            'r.mapcalc',
            '{} = {}'.format(output, expression),
            overwrite=True, run_=False, quiet=True
        )
        
        rc()
    
    elif api == 'grass':
        from pycode.oss  import execmd
        
        rcmd = execmd((
            "r.mapcalc \"{} = {}\" --overwrite --quiet"
        ).format(output, expression))
    
    else:
        raise ValueError("{} is not available!".format(api))
    
    return output


def grs_to_rst(grsRst, rst, as_cmd=None):
    """
    GRASS Raster to Raster
    """
    
    from pycode.geofiles import grs_rst_drv
    from pycode.oss import fprop
    
    rstDrv = grs_rst_drv()
    rstExt = fprop(rst, 'ff')
    
    if not as_cmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            "r.out.gdal", input=grsRst, output=rst,
            format=rstDrv[rstExt], flags='c',
            createopt='TFW=YES',
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from pycode.oss import execmd
        
        rcmd = execmd((
            "r.out.gdal input={} output={} format={} "
            "{} -c --overwrite --quiet"
        ).format(
            grsRst, rst, rstDrv[rstExt],
            "createopt=\"TFW=YES\""
        ))
    
    return rst

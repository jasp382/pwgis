"""
GRASS GIS tools
"""

import os

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


def grsshp_to_grsrst(inshp, src, outrst, cmd=None):
    """
    GRASS Vector to GRASS Raster

    api:
    * pygrass
    * grass

    Vectorial geometry to raster
    
    If source is None, the convertion will be based on the cat field.
    
    If source is a string, the convertion will be based on the field
    with a name equal to the given string.
    
    If source is a numeric value, all cells of the output raster will have
    that same value.
    """

    __USE = "cat" if not src else "attr" if type(src) == str \
        else "val" if type(src) == int or \
        type(src) == float else None
    
    if not __USE:
        raise ValueError('\'source\' parameter value is not valid')
    
    if not cmd:
        from grass.pygrass.modules import Module
            
        m = Module(
            "v.to.rast", input=inshp, output=outrst, use=__USE,
            attribute_column=src if __USE == "attr" else None,
            value=src if __USE == "val" else None,
            overwrite=True, run_=False, quiet=True
        )
            
        m()
    
    else:
        from pycode.oss import execmd
            
        rcmd = execmd((
            "v.to.rast input={} output={} use={}{} "
            "--overwrite --quiet"
        ).format(
            inshp, outrst, __USE,
            "" if __USE == "cat" else f" attribute_column={src}" \
                if __USE == "attr" else f" val={src}"
        ))

    return outrst


def shp_to_grs(inLyr, outLyr, filterByReg=None, asCMD=None):
    """
    Add Shape to GRASS GIS
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
        
        f = 'o' if not filterByReg else 'ro'
        
        m = Module(
            "v.in.ogr", input=inLyr, output=outLyr, flags='o',
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from pycode.oss import execmd
        
        rcmd = execmd((
            "v.in.ogr input={} output={} -o{} --overwrite --quiet"
        ).format(inLyr, outLyr, " -r" if filterByReg else ""))
    
    return outLyr


def category_rules(dic, out_rules):
    """
    Write rules file for reclassify - in this method, categorical values will be
    converted into new designations/values
    
    dic = {
        new_value : old_value,
        new_value : old_value,
        ...
    }
    """
    
    if os.path.splitext(out_rules)[1] != '.txt':
        out_rules = os.path.splitext(out_rules)[0] + '.txt'
    
    with open(out_rules, 'w') as txt:
        for k in dic:
            txt.write(
                '{n}  = {o}\n'.format(o=str(dic[k]), n=str(k))
            )
        
        txt.close()
    
    return out_rules


def rcls_rst(inrst, rclsRules, outrst, api='gdal', maintain_ext=True):
    """
    Reclassify a raster (categorical and floating points)
    
    elif api == grass:
    rclsRules should be a path to a text file
    """
    
    if api == "pygrass":
        from grass.pygrass.modules import Module
        
        r = Module(
            'r.reclass', input=inrst, output=outrst, rules=rclsRules,
            overwrite=True, run_=False, quiet=True
        )
        
        r()
    
    else:
        raise ValueError(f"API {api} is not available")
    
    return outrst


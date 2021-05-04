"""
Run Informative Value Method
"""

def grs_infovalue(movs, _var, refrst, out):
    """
    Informative Value estimation using GRASS GIS
    """

    import os
    import math as m
    from pycode.ext import rstext_to_rst
    from pycode.geofiles import check_isRaster
    from pycode.prop.rst import rst_shape, frequencies
    from pycode.wenv import run_grass
    from pycode.oss import lst_ff, fprop

    # Get reference raster
    ws = os.path.dirname(out)
    
    refrst = rstext_to_rst(refrst, os.path.join(ws, 'refrst.tif'))

    if type(_var) != list:
        # List raster files
        rstvar = lst_ff(_var, file_format='tif')
    
    else:
        rstvar = _var

    # Get Reference raster shape (number of rows and columns)
    refshape = rst_shape(refrst)

    # Get Variables Rasters Shape and see if there is any difference
    # comparing with reference
    varshp = rst_shape(rstvar)

    for r in varshp:
        if varshp[r] != refshape:
            raise ValueError((
                f'All rasters must have the same dimension! '
                f'{r} have different shape when compared with refrst!'
            ))
    
    # Start GRASS GIS Session
    # Get name for GRASS GIS location
    loc = fprop(movs, 'fn', forceLower=True)[:7] + '_loc'

    # Create GRASS GIS location
    gbase = run_grass(ws, location=loc, srs=refrst)

    # Start GRASS GIS Session
    import grass.script.setup as gsetup

    gsetup.init(gbase, ws, loc, 'PERMANENT')

    # Import GRASS GIS modules
    from pycode.grstools import grsshp_to_grsrst
    from pycode.grstools import shp_to_grs
    from pycode.grstools import rst_to_grs, grs_to_rst
    from pycode.grstools import rstcalc
    from pycode.grstools import category_rules, rcls_rst

    # Check if movs are raster
    is_rst = check_isRaster(movs)

    if is_rst:
        movrst = rst_to_grs(movs, fprop(movs, 'fn', forceLower=True))

    else:
        movshp = shp_to_grs(movs, fprop(movs, 'fn', forceLower=True), asCMD=True)
    
        # To raster
        movrst = grsshp_to_grsrst(movshp, 1, f'rst_{movshp}', cmd=True)
    
    # Add rasters to GRASS GIS
    grsvar = [rst_to_grs(r, fprop(r, 'fn', forceLower=True)) for r in rstvar]

    # Get raster representing areas with values in all rasters
    gref = rst_to_grs(refrst, 'refrst')

    i = 1
    for r in grsvar:
        gref = rstcalc(f"int({r} * {gref})", f"refrst_{str(i)}", api='grass')

        i += 1
    
    # Ensure that we have only cells with data in all rasters
    refrules = category_rules({0 : 1}, os.path.join(ws, loc, 'refrules.txt'))

    gref = rcls_rst(gref, refrules, f'rcls_{gref}', api="pygrass")

    grsvar = [rstcalc(f"{r} * {gref}", f"{r}_san", api='grass') for r in grsvar]

    # Export rasters to get frequencies
    filevar = {r : grs_to_rst(r, os.path.join(
        ws, loc, f"{r}.tif"
    ), as_cmd=True) for r in grsvar}

    # Get raster frequencies
    # Negative nodata values are not allowed
    rstfreq = {r : frequencies(filevar[r]) for r in filevar}

    # Count total cells
    i = 0
    for r in rstfreq:
        if not i:
            totalcells = 0
            for v in rstfreq[r]:
                totalcells += rstfreq[r][v]
        
            i += 1
    
        else:
            __totalcells = 0
            for v in rstfreq[r]:
                __totalcells += rstfreq[r][v]
        
            if __totalcells != totalcells:
                raise ValueError(f'{r} has a different number of cells with data')
    
    # Intersect landslides raster with var rasters
    varwithmov = [rstcalc(f"{movrst} * {r}", f"mov_{r}", api='grass') for r in grsvar]

    # Export rasters to get frequencies
    filemov = {grsvar[i] : grs_to_rst(varwithmov[i], os.path.join(
        ws, loc, f"{varwithmov[i]}.tif"
    ), as_cmd=True) for i in range(len(varwithmov))}

    # Get raster frequencies
    rstmovfreq = {r : frequencies(filemov[r]) for r in filemov}

    # Count total cells with landslides
    i = 0
    for r in rstmovfreq:
        if not i:
            totalmov = 0
            for v in rstmovfreq[r]:
                totalmov += rstmovfreq[r][v]
        
            i += 1
    
        else:
            __totalmov = 0
            for v in rstmovfreq[r]:
                __totalmov += rstmovfreq[r][v]
        
            if __totalmov != totalmov:
                raise ValueError(f'{r} has a different number of cells with data')

    # Estimate VI for each class of every variable
    vi = {}

    denom = totalmov / totalcells
    for r in rstfreq:
        vi[r] = {}
        for cls in rstfreq[r]:
            if cls in rstmovfreq[r]:
                vi[r][cls] = m.log10(
                    (rstmovfreq[r][cls] / rstfreq[r][cls]) / denom
                )
        
            else:
                vi[r][cls] = 9999
    
    # Replace Classes without VI, from 9999 to minimum VI
    vis = []
    for d in vi.values():
        vis += d.values()
    
    min_vi = int(round(min(vis), 4) * 10000)

    for r in vi:
        for cls in vi[r]:
            if vi[r][cls] == 9999:
                vi[r][cls] = min_vi
            else:
                vi[r][cls] = int(round(vi[r][cls], 4) * 10000)
    
    # Reclassify
    vivar = []
    for r in grsvar:
        rules = category_rules(
            vi[r], os.path.join(ws, loc, f'vi_{r}.txt')
        )

        virst = rcls_rst(r, rules, f'vi_{r}', api="pygrass")
    
        vivar.append(virst)

    # Integer to float
    virst = [rstcalc(
        f"{r} / 10000.0", f"{r}_f", api='grass'
    ) for r in vivar]

    # Sum results
    virstfinal = rstcalc(" + ".join(virst), fprop(out, 'fn'), api='grass')

    fffinal = grs_to_rst(virstfinal, out)

    return out


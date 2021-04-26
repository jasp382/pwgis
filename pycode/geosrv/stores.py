"""
Tools for Geoserver datastores management
"""


def shp_to_store(shape, store_name, workspace):
    """
    Create a new datastore
    """

    import os;         import requests
    from pycode.geosrv import con_gsrv

    conf = con_gsrv()

    url = (
        '{pro}://{host}:{port}/geoserver/rest/workspaces/{work}/datastores/'
        '{store}/file.shp'
        ).format(
            host=conf['HOST'], port=conf['PORT'], work=workspace,
            store=store_name, pro=conf['PROTOCOL']
        )
    
    fn, ff = os.path.splitext(os.path.basename(shape))

    if ff != '.zip':
        from pycode.zzip import zip_files

        shp_fld = os.path.dirname(shape)

        ff = []
        for (d, _d_, f) in os.walk(shp_fld):
            ff.extend(f)
            break

        shapefiles = [os.path.join(
            shp_fld, f
        ) for f in ff if os.path.splitext(f)[0] == fn]

        shape = os.path.join(shp_fld, fn + '.zip')
        zip_files(shapefiles, shape)

    with open(shape, 'rb') as f:
        r = requests.put(
            url,
            data=f,
            headers={'content-type': 'application/zip'},
            auth=(conf['USER'], conf['PASSWORD'])
        )

        return r


def lst_stores(workspace):
    """
    List all stores in a Workspace
    """
    
    import requests
    from pycode.geosrv import con_gsrv
    
    conf = con_gsrv()
    
    url = '{pro}://{host}:{port}/geoserver/rest/workspaces/{work}/datastores'.format(
        host=conf['HOST'], port=conf['PORT'], work=workspace, pro=conf['PROTOCOL']
    )
    
    r = requests.get(
        url, headers={'Accept': 'application/json'},
        auth=(conf['USER'], conf['PASSWORD'])
    )
    
    ds = r.json()
    if 'dataStore' in ds['dataStores']:
        return [__ds['name'] for __ds in ds['dataStores']['dataStore']]
    else:
        return []


def del_store(workspace, name):
    """
    Delete an existing Geoserver datastore
    """
    
    import requests
    from pycode.geosrv import con_gsrv
    
    conf = con_gsrv()
    
    url = (
        '{pro}://{host}:{port}/geoserver/rest/workspaces/{work}/'
        'datastores/{ds}?recurse=true'
    ).format(
        host=conf['HOST'], port=conf['PORT'], work=workspace, ds=name,
        pro=conf['PROTOCOL']
    )
    
    r = requests.delete(url, auth=(conf['USER'], conf['PASSWORD']))
    
    return r


def add_rst_store(raster, store_name, workspace):
    """
    Create a new store with a raster layer
    """
    
    import os;         import requests
    from pycode.Xml    import write_xml_tree
    from pycode.geosrv import con_gsrv
    from pycode.char   import random_str
    
    conf = con_gsrv()
    
    url = (
        '{pro}://{host}:{port}/geoserver/rest/workspaces/{work}/'
        'coveragestores?configure=all'
    ).format(
        host=conf['HOST'], port=conf['PORT'],
        work=workspace, pro=conf['PROTOCOL']
    )
    
    # Create obj with data to be written in the xml
    xmlTree = {
        "coverageStore" : {
            "name"   : store_name,
            "workspace": workspace,
            "enabled": "true",
            "type"   : "GeoTIFF",
            "url"    : raster
        }
    }
    
    treeOrder = {
        "coverageStore" : ["name", "workspace", "enabled", "type", "url"]
    }
    
    # Write XML
    xml_file = write_xml_tree(xmlTree,os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'tmpxml', f'st_{random_str(7)}.xml'
    ), nodes_order=treeOrder)
    
    # Send request
    with open(xml_file, 'rb') as f:
        r = requests.post(
            url,
            data=f,
            headers={'content-type': 'text/xml'},
            auth=(conf['USER'], conf['PASSWORD'])
        )
    
    os.remove(xml_file)
        
    return r


"""
Tools for Geoserver layers management
"""


def lst_lyr():
    """
    List all layers in the geoserver
    """

    import requests
    from pycode.geosrv import con_gsrv

    conf = con_gsrv()

    url = '{pro}://{host}:{port}/geoserver/rest/layers'.format(
        host=conf['HOST'], port=conf['PORT'], pro=conf['PROTOCOL']
    )

    r = requests.get(
        url, headers={'Accept': 'application/json'},
        auth=(conf['USER'], conf['PASSWORD'])
    )

    layers = r.json()

    return [l['name'] for l in layers['layers']['layer']]


def pub_rst_lyr(layername, datastore, workspace, epsg_code):
    """
    Publish a Raster layer
    """
    
    import os;         import requests
    from pycode.char   import random_str
    from pycode.Xml    import write_xml_tree
    from pycode.prj    import epsg_to_wkt
    from pycode.geosrv import con_gsrv

    conf = con_gsrv()
    
    url = (
        '{pro}://{host}:{port}/geoserver/rest/workspaces/{work}/'
        'coveragestores/{storename}/coverages'
    ).format(
        host=conf['HOST'], port=conf['PORT'],
        work=workspace, storename=datastore, pro=conf['PROTOCOL']
    )
    
    # Create obj with data to be written in the xml
    xmlTree = {
        "coverage" : {
            "name"      : layername,
            "title"     : layername,
            "nativeCRS" : str(epsg_to_wkt(epsg_code)),
            "srs"       : 'EPSG:{}'.format(str(epsg_code)),
        }
    }
    
    # Write XML
    xml_file = write_xml_tree(xmlTree, os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'tmpxml', f'ly_{random_str(7)}.xml'
    ))
    
    # Create layer
    with open(xml_file, 'rb') as f:
        r = requests.post(
            url, data=f,
            headers={'content-type': 'text/xml'},
            auth=(conf['USER'], conf['PASSWORD'])
        )
    
    return r


def del_lyr(lyr):
    """
    Delete some layer
    """
    
    import requests
    from pycode.geosrv import con_gsrv

    conf = con_gsrv()
    
    url = '{}://{}:{}/geoserver/rest/layers/{}'.format(
        conf['PROTOCOL'], conf["HOST"], conf["PORT"], lyr
    )
    
    r = requests.delete(url, auth=(conf["USER"], conf["PASSWORD"]))
    
    return r


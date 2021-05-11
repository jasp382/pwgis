from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.
def home_redirect(request):
    from django.http import HttpResponseRedirect
    
    return HttpResponseRedirect('/landslide/')


def inputs_view(request):
    from landslides.forms import InputsForm
    
    riskform = InputsForm()
    
    return render(
        request, 'landslides/risk_inputs.html',
        {'risk_form': riskform}
    )


def map_production(request):
    import os
    import random
    from django.http import HttpResponseRedirect
    from pycode.djg import save_geodata

    if request.method == "POST":
        # If method is post, there is a form with data

        # Create a new folder to save files
        chars = '0123456789qwertyuiopasdfghjklzxcvbnm'
        fname = ''
        for i in range(10):
            fname += random.choice(chars)
        
        data_folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'data', fname
        )
        os.mkdir(data_folder)

        # Save GeoFiles
        landslides = save_geodata(
            request, 'landslides', data_folder,
            return_only_one_file=True
        )

        variables = save_geodata(
            request, 'variables', data_folder
        )

        from pycode.lndslides import grs_infovalue

        virst = grs_infovalue(
            landslides, variables, variables[0],
            os.path.join(data_folder, 'new_vi_map.tif')
        )

        # Send data to GeoServer
        from pycode.geosrv.ws import create_ws
        from pycode.geosrv.stores import add_rst_store
        from pycode.geosrv.lyrs import pub_rst_lyr
        from pycode.geosrv.sty import create_style
        from pycode.geosrv.sty import assign_style_to_layer
        from pycode.prop.prj import get_rst_epsg

        # Create new workspace
        workspace = os.path.basename(data_folder)
        create_ws(workspace)

        # Create raster store
        stname = workspace + '_vimap'
        gsrv_vi = (
            f'/home/geoserveruser/riskservice/landslides/data/{workspace}/'
            f'{os.path.basename(virst)}'
        )
        add_rst_store(gsrv_vi, stname, workspace)

        # Publish Layer
        lyrname = workspace + '_vilayer'
        pub_rst_lyr(lyrname, stname, workspace, get_rst_epsg(virst))

        # Generate Style
        from pycode.prop.rst import rst_stats
        from pycode.geosrv.sld import write_raster_sld

        stats = rst_stats(virst) # Obtem estatisticas do mapa
        N_CLASSES = 5 # Number classes

        mmin, mmax = stats['MIN'], stats["MAX"]

        # Calculo amplitude da classe
        int_break = (mmax - mmin) / N_CLASSES

        COLOR = [
            (0, 245, 17), (138, 249, 18), (234, 247, 17),
            (248, 160, 0), (249, 15, 0)
        ]

        breaks = []
        for i in range(N_CLASSES):
            if not i:
                breaks.append(mmin + int_break)
            else:
                breaks.append(breaks[i-1] + int_break)
        
        SYMBOLOGY_RULES = {round(breaks[i], 2) : {
            "COLOR" : COLOR[i], "OPACITY" : 0.95, "LABEL" : "{} - {}".format(
                round(mmin, 3) if not i else round(breaks[i-1], 3),
                round(breaks[i], 3)
            )
        } for i in range(N_CLASSES)}

        sldfile = write_raster_sld(
            SYMBOLOGY_RULES, os.path.join(data_folder, 'map_sld.sld'),
            dataType="FLOATING"
        )

        STYLE_NAME = f'dem_{workspace}'
        create_style(STYLE_NAME, sldfile)
        publish_status = assign_style_to_layer(STYLE_NAME, lyrname)


        return HttpResponseRedirect((
            f'/mapviewer/?workspace={workspace}&'
            f'layer={lyrname}&style={STYLE_NAME}'
        ))
    
    else:
        return HttpResponseRedirect('/landslide/')


def map_viewer(request):
    """
    Render result
    """
    
    return render(request, 'landslides/map_result.html')


def get_wms(request, work):
    """
    Get WMS
    """

    import requests
    from django.http import HttpResponse
    from riskservice.settings import GEOSERVER_CON

    r = requests.get('http://{}:{}/geoserver/{}/wms?'.format(
        GEOSERVER_CON['HOST'], GEOSERVER_CON['PORT'], work
    ),params={
        'service'     : request.GET['service'],
        'version'     : request.GET['version'],
        'request'     : request.GET['request'],
        'layers'      : request.GET['layers'],
        'width'       : request.GET['width'],
        'height'      : request.GET['height'],
        'bbox'        : request.GET['bbox'],
        'format'      : request.GET['format'],
        'transparent' : request.GET['transparent'],
        'styles'      : request.GET['styles'],
        'srs'         : request.GET['srs']
    })

    return HttpResponse(r.content)


def get_extent(request, work, lyr):
    """
    Get Capabilities View
    """

    import requests
    import xmltodict
    from django.http import JsonResponse
    from riskservice.settings import GEOSERVER_CON

    # Get XML Data
    xml_data = requests.get((
        'http://{}:{}/geoserver/wms?request=GetCapabilities&'
        'service=WMS&version=1.1.1'
    ).format(
        GEOSERVER_CON['HOST'], GEOSERVER_CON['PORT']
    ), allow_redirects=True)

    # XML to Dict
    dict_data = xmltodict.parse(xml_data.content)

    # Get Layer Information
    LYR_NAME = '{}:{}'.format(work, lyr)
    lyrs_data = dict_data['WMT_MS_Capabilities']['Capability']['Layer']['Layer']

    # Get Response data
    resp = {}
    for k in lyrs_data:
        if k['Name'] == LYR_NAME:
            resp['min_x'] = k['LatLonBoundingBox']['@minx']
            resp['max_x'] = k['LatLonBoundingBox']['@maxx']
            resp['min_y'] = k['LatLonBoundingBox']['@miny']
            resp['max_y'] = k['LatLonBoundingBox']['@maxy']
    
    return JsonResponse(resp, content_type='json')

def get_wfs(request, work, lyr):
    """
    GeoServer - Pass WFS using Django
    """

    import requests
    from django.http         import JsonResponse
    from riskservice.settings import GEOSERVER_CON

    if 'val' in request.GET and 'attr' in request.GET:
        _q = '&cql_filter={}=\'{}\''.format(
            request.GET['attr'], request.GET['val']
        )

    else:
        _q = ''
    
    if 'count' in request.GET:
        _c = '&count={}'.format(str(request.GET['count']))
    else:
        _c = ''

    url = (
        'http://{host}:{port}/geoserver/{work_}/ows?'
        'service=WFS&version=2.0.0&request=GetFeature&'
        'typeName={work_}:{lyrn}&outputFormat=application/json'
        '{c}{q}'
    ).format(
        host=GEOSERVER_CON['HOST'], port=GEOSERVER_CON['PORT'],
        work_=work, lyrn=lyr, q=_q, c=_c
    )

    r = requests.get(url, headers={'Accept' : 'application/json'})
    wfs = r.json()

    return JsonResponse(wfs, content_type='json')


def get_featinfo(request, work, lyr):
    """
    Geoserver getFeatureInfo data to a Json Response
    """

    import requests
    from django.http import JsonResponse
    from riskservice.settings import GEOSERVER_CON

    url = (
        'http://{host}:{port}/geoserver/wfs?'
        'INFO_FORMAT=application/json&'
        'REQUEST=GetFeatureInfo&EXCEPTIONS=application/vnd.ogc.se_xml&'
        'SERVICE=WMS&VERSION=1.1.1&'
        'WIDTH={width}&HEIGHT={height}&'
        'X={x}&Y={y}&BBOX={bbox}&LAYERS={work}:{lyr}&'
        'QUERY_LAYERS={work}:{lyr}&TYPENAME={work}:{lyr}&'
        'CRS=EPSG:4326'
    ).format(
        host=GEOSERVER_CON['HOST'], port=GEOSERVER_CON['PORT'],
        work=work, lyr=lyr,
        width=request.GET['WIDTH'], height=request.GET['HEIGHT'],
        x=request.GET['X'], y=request.GET['Y'],
        bbox=request.GET['BBOX']
    )

    r = requests.get(url, headers={'Accept': 'application/json'})

    return JsonResponse(r.json())

def get_legend(request, work, lyr, style):
    """
    Get Layer Legend
    """

    import requests
    from django.http import JsonResponse
    from riskservice.settings import GEOSERVER_CON

    url = (
        'http://{host}:{port}/geoserver/wms?REQUEST=GetLegendGraphic&'
        'VERSION=1.0.0&FORMAT=application/json'
        '&LAYER={w}:{l}&style={s}'
    ).format(
        host=GEOSERVER_CON['HOST'], port=GEOSERVER_CON['PORT'],
        w=work, l=lyr, s=style
    )

    r = requests.get(url, headers={'Accept' : 'application/json'})

    return JsonResponse(r.json())


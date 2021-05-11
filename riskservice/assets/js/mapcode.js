// get Variables using URL
var url = new URL(window.location.href),
	workspace = url.searchParams.get("workspace"),
	layer = url.searchParams.get("layer")
	style = url.searchParams.get("style");

// create Map
var mymap = L.map('map');

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
	maxZoom: 18,
	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
		'<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
		'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
	id: 'mapbox/streets-v11',
	tileSize: 512,
	zoomOffset: -1
}).addTo(mymap);

// Add DEM WMS
var wms_url = '/api/wms/' + workspace + '?';

var wmsLayer = L.tileLayer.wms(wms_url, {
    layers : layer,
    format : 'image/png',
    transparent: true,
    styles : style
});

mymap.addLayer(wmsLayer);

// Get and Set Map Extent
var url_extent = '/api/extent/' + workspace + '/' + layer + '/';
var extent = undefined;

$(document).ready(function () {
	$.getJSON(url_extent, function(result) {
		extent = result;

		var topleft = L.latLng(extent['max_y'], extent['min_x']),
			lowerright = L.latLng(extent['min_y'], extent['max_x']);
		
		var bounds = L.latLngBounds(topleft, lowerright);

		mymap.fitBounds(bounds);
	});
});

// Get Feature Info
mymap.on('click', function (event) {
	var clickPnt = mymap.latLngToContainerPoint(event.latlng, mymap.getZoom()),
		size     = mymap.getSize(),
		mdtinfo  = '/api/featinfo/' + workspace + '/' + layer + '/?WIDTH=' + String(size.x) +
			'&HEIGHT=' + String(size.y) + '&X=' + String(clickPnt.x) +
			'&Y=' + String(clickPnt.y) +
			'&BBOX=' + String(mymap.getBounds().toBBoxString());
		
	$(document).ready(function () {
		$.getJSON(mdtinfo, function (data) {
			var popup = L.popup(),
				feat  = data.features[0];
			
			if (!feat) return;
					
			popup
				.setLatLng(event.latlng)
				.setContent(
					"<p><b>Altitude: </b>" + String(feat.properties.GRAY_INDEX) + '</p>'
				).openOn(mymap);
		});
	});
});

// Get Legend
var lurl = '/api/legend/' + workspace + '/' + layer + '/' + style + '/',
	leg = undefined;

$(document).ready(function () {
	$.getJSON(lurl, function(result) {
		leg = result.Legend[0].rules[0].symbolizers[0].Raster.colormap.entries;

		var legend = L.control({'position' : 'bottomright'});

		legend.onAdd = function (mymap) {
			var div = L.DomUtil.create('div', 'info legend'),
				labels = [];

			for (var i = 0; i < leg.length; i++) {
				labels.push(
					'<i style="background:' + leg[i].color + '"></i>' + leg[i].label
				);
			}

			div.innerHTML = labels.join('<br>');

			return div;
		}

		legend.addTo(mymap);
	});
});
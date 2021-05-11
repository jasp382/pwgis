"""riskservice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from landslides.views import home_redirect
from landslides.views import inputs_view
from landslides.views import map_production
from landslides.views import map_viewer
from landslides.views import get_extent, get_wfs, get_wms, get_featinfo, get_legend

urlpatterns = [
    path('', home_redirect, name='redirect'),
    path('landslide/', inputs_view, name='landslide-inputs'),
    path('map-prod/', map_production, name='landslide-prod'),
    path('mapviewer/', map_viewer, name='landslide-map'),
    path('api/wfs/<str:work>/<str:lyr>/', get_wfs, name='api_wfs'),
    path('api/extent/<str:work>/<str:lyr>/', get_extent, name='api-extent'),
    path('api/featinfo/<str:work>/<str:lyr>/', get_featinfo, name='api-featinfo'),
    path('api/wms/<str:work>/', get_wms, name='api-wms'),
    path('api/legend/<str:work>/<str:lyr>/<str:style>/', get_legend, name='api-legend'),
    path('admin/', admin.site.urls),
]

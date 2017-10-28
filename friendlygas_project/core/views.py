# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse
from orionclient import OrionClient
import json

from django.shortcuts import render
# Create your views here.

def index(request):
	template_name = 'core/home.html'
	return render(request, template_name, {})

def location_request(request):
	latitude = request.GET.get('latitude', None)
	longitude = request.GET.get('longitude', None)
	template_name = 'core/home.html'
	context = {
		'latitude': latitude,
		'longitude': longitude
	}
	return JsonResponse(context)
	# return render(request, template_name, context)

def get_orion_client():
	client = OrionClient(
            orion_host_url='104.131.81.74',
            orion_host_port='1026',
            authMethod=None,
            username='root',
            password='violao123',
            orion_token_url=None,
            )
	return client

def near_gas_stations(request):
	# latitude = request.POST['latitude']
	# longitude = request.POST['longitude']
	# radius = request.POST['radius']
	latitude = request.GET.get('latitude', None)
	longitude = request.GET.get('longitude', None)
	radius = request.GET.get('radius', None)
	orion_client = get_orion_client()
	near_gas_stations = orion_client.query_entity('GasStation', latitude, longitude, radius)
	return JsonResponse(near_gas_stations)
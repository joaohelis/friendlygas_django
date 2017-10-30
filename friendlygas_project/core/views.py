# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse
from orionclient import OrionClient
import json
import datetime
import pytz

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
            username='root',
            password='violao123',
			authMethod=None,            
			orion_token_url=None,
            )
	return client

def near_gas_stations(request):
	latitude = request.GET.get('latitude', None)
	longitude = request.GET.get('longitude', None)
	radius = request.GET.get('radius', None)
	orion_client = get_orion_client()
	near_gas_stations = orion_client.query_entity('GasStation', latitude, longitude, radius)	
	return JsonResponse(near_gas_stations)


def update_entity_attributes(request):
	orion_client = get_orion_client()
	entity_id = request.GET.get('entity_id', None)
	price = request.GET.get('price', None)
	star_votes1 = request.GET.get('star_votes[1]', None)
	star_votes2 = request.GET.get('star_votes[2]', None)
	star_votes3 = request.GET.get('star_votes[3]', None)
	star_votes4 = request.GET.get('star_votes[4]', None)
	star_votes5 = request.GET.get('star_votes[5]', None)
	dateUpdated = str(datetime.datetime.now(pytz.timezone('America/Recife')))
	attributes = '{ "last_update" : "' + dateUpdated + '", "price" : ' + price + ', "star_votes" : {"1":' + star_votes1 + ', "2":' + star_votes2 +', "3":' + star_votes3 + ', "4": ' + star_votes4  + ', "5": ' + star_votes5 + '}}'
	attrs = json.loads(attributes)
	try:
		orion_client.update_attributes(entity_id, attrs)
		response['code'] = 'OK'
	except:
		response['code'] = 'ERROR'
	return JsonResponse(response)


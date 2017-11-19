# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse
from orionclient import OrionClient
from django.conf import settings
import json
import datetime
import pytz
import csv
import os
from ckanapi import RemoteCKAN
from django.contrib.staticfiles.storage import staticfiles_storage
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

def save_gas_stations_as_csv(orion_client):    
	csv_header = []
	csv_rows = []  
	gas_stations = orion_client.fetch_entity(type_id='GasStation')
	for gas_station_key in gas_stations:
		gas_station = orion_client.fetch_entity(type_id='GasStation', entity_id=gas_station_key)
		gas_station.pop('star_votes', None)
		if not csv_header:
			csv_header.append(gas_station.keys())        
		csv_rows.append(list(gas_station.values()))
	file_name = 'gas_stations_%s.csv' % datetime.datetime.now().__str__()
	file_path = 'friendlygas_project/core/media/' + file_name	
	with open(file_path, "wb") as f:
		writer = csv.writer(f)
		writer.writerows(csv_header + csv_rows)
	return file_name

def gas_stations_json(orion_client):
	json_file_path = 'friendlygas_project/core/media/gas_stations_data.json'
	if not os.path.isfile(json_file_path):		
		gas_stations = orion_client.fetch_entity(type_id='GasStation')
		gas_stations_map = {}
		for gas_station_key in gas_stations:
			gas_station = orion_client.fetch_entity(type_id='GasStation', entity_id=gas_station_key)
			gas_stations_map[gas_station_key] = gas_stations[gas_station_key]
		js = json.dumps(gas_stations_map, sort_keys=True, indent=4, separators=(',', ': '))
		with open(json_file_path, 'w') as f:
		    f.write(js)
	return json_file_path

def save_map_as_csv(gas_stations_map):
	csv_header = []
	csv_rows = []
	for key, value in gas_stations_map.items():		
		value.pop('star_votes', None)
		if not csv_header:
			csv_header.append(value.keys())        
		csv_rows.append(list(value.values()))
	file_name = 'gas_stations_%s.csv' % datetime.datetime.now().__str__()
	file_path = 'friendlygas_project/core/media/' + file_name	
	with open(file_path, "wb") as f:
		writer = csv.writer(f)
		writer.writerows(csv_header + csv_rows)
	return file_name

def update_json_and_save_csv(orion_client, entity_id):
	json_file_path = gas_stations_json(orion_client)
	gas_stations_map = json.load(open(json_file_path))
	gas_station = orion_client.fetch_entity(type_id='GasStation', entity_id=entity_id)	
	gas_stations_map[entity_id] = gas_station
	js = json.dumps(gas_stations_map, sort_keys=True, indent=4, separators=(',', ': '))
	with open(json_file_path, 'w') as f:
		f.write(js)
	return save_map_as_csv(gas_stations_map)

def update_ckan_database_resource(domain, entity_id):
	ua = 'ckanapiexample/1.0 (+http://example.com/my/website)'	
	client = RemoteCKAN('http://104.236.54.23', apikey='eb5346ab-0c53-4b1f-a0a4-f4be797db23b', user_agent=ua)
	# file_name = save_gas_stations_as_csv(get_orion_client())
	file_name = update_json_and_save_csv(get_orion_client(), entity_id)
	date = str(datetime.datetime.now(pytz.timezone('America/Recife')))
	client.action.resource_create(	
	    package_id='ac335d1a-098c-4f18-882c-03950ddc5d7c',
	    name = 'Postos de Combustíveis - Natal - RN - ' + date,
	    description = 'Este arquivo contém as informações dos Postos de Combustíveis de Natal - RN.',
	    format = 'csv',
	    url = 'http://' + domain + '/' + 'media' + '/' + file_name)

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
	response = {}
	try:
		orion_client.update_attributes(entity_id, attrs)
		response['code'] = 'OK'
	except:
		response['code'] = 'ERROR'
	domain = request.get_host()
	update_ckan_database_resource(domain, entity_id)
	return JsonResponse(response)

def update_ckan(request):
	domain = request.get_host()
	update_ckan_database_resource(domain)
	response = {'code': 'OK'}
	return JsonResponse(response) 
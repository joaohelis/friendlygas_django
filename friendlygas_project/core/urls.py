from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^ajax/location_request/$', views.location_request, name='location_request'),
	url(r'^ajax/near_gas_stations/$', views.near_gas_stations, name='near_gas_stations'),
	url(r'^ajax/update_entity_attributes$', views.update_entity_attributes, name='update_entity_attributes'),
]
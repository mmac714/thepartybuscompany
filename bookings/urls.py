"""Defines URL patterns for bookings."""

from django.conf.urls import url

from . import views

from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView


urlpatterns = [
	# Home page
	url(r'^$', views.home, name='home'),

	# Static pages
	url(r'^prices/$', views.prices, name='prices'),
	url(r'^buses/$', views.buses, name='buses'),
	url(r'^specials/$', views.specials, name='specials'),
	url(r'^highdemand/$', views.highdemand, name='highdemand'),
	url(r'^contact/$', views.contact, name='contact'),

	# dynamic pages
	url(r'^reservation/(?P<reservation_id>[0-9a-f-]+)/$', 
		views.reservation, name='reservation'),

	url(r'^quote_form/$', views.quote_form, name='quote_form'),
	url(r'^quote/(?P<reservation_id>[0-9a-f-]+)/$', 
		views.quote, name='quote'),
	url(r'^quote_no_reservation/(?P<reservation_id>[0-9a-f-]+)/$', views.quote_no_reservation,
		name='quote_no_reservation'),


	url(r'^backend-reservation/$', views.backend_reservation, 
		name='backend_reservation'),
	url(r'^payment/(?P<reservation_id>[0-9a-f-]+)/$', views.payment, name='payment'),
	url(r'^confirmation/(?P<reservation_id>[0-9a-f-]+)/$', views.confirmation, 
		name='confirmation'),
	
	url(r'^booking/(?P<reservation_id>[0-9a-f-]+)/$',
		views.booking, name='booking'),
	url(r'^invoice/(?P<reservation_id>[0-9a-f-]+)/$',
		views.invoice, name='invoice'),
	url(r'^booking_list/$', views.booking_list, name='booking_list'),
	url(r'^survey_list/$', views.survey_list, name='survey_list'),


	url(r'^sitemap\.xml$', views.sitemap, name="sitemap"),
	url(r'^favicon.ico$', 
		RedirectView.as_view(url=staticfiles_storage.url('logo.png'),
			permanent=False),
		name="favicon"),

]
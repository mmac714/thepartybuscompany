"""Defines URL patterns for bookings."""

from django.conf.urls import url

from . import views

urlpatterns = [
	# Home page
	url(r'^$', views.home, name='home'),

	# Static pages
	url(r'^prices/$', views.prices, name='prices'),
	url(r'^buses/$', views.buses, name='buses'),
	url(r'^specials/$', views.specials, name='specials'),
	url(r'^highdemand/$', views.highdemand, name='highdemand'),

	# dynamic pages
	url(r'^reservation/$', views.reservation, name='reservation'),
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
	url(r'^sitemap\.xml$', views.sitemap, name="sitemap")

]
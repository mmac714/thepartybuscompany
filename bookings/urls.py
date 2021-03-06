"""Defines URL patterns for bookings."""

from django.conf.urls import url

from . import views

from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView


urlpatterns = [

	###############
	# Static pages
	###############
	url(r'^prices/$', views.prices, name='prices'),
	url(r'^highdemand/$', views.highdemand, name='highdemand'),
	url(r'^more_than_sixty_days/$', views.more_than_sixty_days,
		name='more_than_sixty_days'),
	url(r'^contact/$', views.contact, name='contact'),
	url(r'^under_construction/$', views.under_construction, 
		name='under_construction'),

	###############
	# dynamic pages
	###############
	url(r'^$', views.home, name='home'),

	url(r'^reservation_form/(?P<reservation_id>[0-9a-f-]+)/$', 
		views.reservation_form, 
		name='reservation_form'),

	url(r'^quote/(?P<reservation_id>[0-9a-f-]+)/$', 
		views.quote, 
		name='quote'),

	# Not using this right now.
	url(r'^quote_no_reservation/(?P<reservation_id>[0-9a-f-]+)/$', 
		views.quote_no_reservation,
		name='quote_no_reservation'),

	url(r'^price_form/$', views.price_form, name='price_form'),

	url(r'^select_bus_link/(?P<bus>\d+)/$',
		views.select_bus_link,
		name='select_bus_link'),


	url(r'^backend-reservation/$', views.backend_reservation, 
		name='backend_reservation'),
	url(r'^payment/(?P<reservation_id>[0-9a-f-]+)/$', views.payment, name='payment'),
	url(r'^confirmation/(?P<reservation_id>[0-9a-f-]+)/$', views.confirmation, 
		name='confirmation'),
	
	url(r'^booking/(?P<reservation_id>[0-9a-f-]+)/$',
		views.booking, name='booking'),

	url(r'^invoice/(?P<reservation_id>[0-9a-f-]+)/$',
		views.invoice, name='invoice'),

	###############
	# Emails
	###############

	url(r'^send_follow_up_email/(?P<reservation_id>[0-9a-f-]+)/$',
		views.send_follow_up_email, name='send_follow_up_email'),
	url(r'^send_deposit_link_email/(?P<reservation_id>[0-9a-f-]+)/$',
		views.send_deposit_link_email, name='send_deposit_link_email'),

	###############
	# List pages
	###############

	url(r'^reservation/(?P<reservation_id>\d+)/comment/$', views.add_comment_to_post, 
		name='add_comment_to_post'),

	###############
	# List pages
	###############
	url(r'^booking_list/$', views.booking_list, name='booking_list'),
	url(r'^survey_list/$', views.survey_list, name='survey_list'),
	url(r'^completed_reservation_list/$', 
		views.completed_reservation_list, 
		name='completed_reservation_list'),

	url(r'^payment_no_deposit_list/$', 
		views.payment_no_deposit_list, 
		name='payment_no_deposit_list'),

	url(r'^payment_paid_deposit_list/$', 
		views.payment_paid_deposit_list, 
		name='payment_paid_deposit_list'),

	url(r'^payment_completed_list/$', 
		views.payment_completed_list, 
		name='payment_completed_list'),

	url(r'^reservations_upcoming_list/$',
		views.reservations_upcoming_list,
		name='reservations_upcoming_list'),



	###############
	# Creation pages
	###############
	url(r'^vehicle_management/$', views.vehicle_management,
		name='vehicle_management'),
	
	url(r'^driver_management/$', views.driver_management,
		name='driver_management'),

	url(r'^affiliate_management/$', views.affiliate_management,
		name='affiliate_management'),

	###############
	# Profile pages
	###############
	url(r'vehicle_profile/(?P<vehicle_id>[0-9a-f-]+)/$', views.vehicle_profile,
		name='vehicle_profile'),

	url(r'affiliate_profile/(?P<affiliate_id>[0-9a-f-]+)/$', views.affiliate_profile,
		name='affiliate_profile'),

	url(r'driver_profile/(?P<driver_id>[0-9a-f-]+)/$', views.driver_profile,
		name='driver_profile'),

	url(r'^price_calculator_form/$', 
		views.price_calculator_form,
		name='price_calculator_form'),



	url(r'^sitemap\.xml$', views.sitemap, name="sitemap"),
	url(r'^customer_agreement\.pdf$',
	views.customer_agreement, name="customer_agreement"),

	url(r'^favicon.ico$', 
		RedirectView.as_view(url=staticfiles_storage.url('logo.png'),
			permanent=False),
		name="favicon"),

]
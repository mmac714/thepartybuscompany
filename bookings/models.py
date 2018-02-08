from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect, reverse
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context

import datetime, time

import stripe
import uuid

from pb_config.settings import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'bus_{0}/{1}'.format(instance.bus.id, filename)

class Affiliate(models.Model):
	name = models.CharField(max_length=100)
	contact = models.CharField(max_length=100)

	def __str__(self):
		""" Return the name of the affiliate """
		return str(self.name)

class Driver(models.Model):
	name = models.CharField(max_length=100)
	contact = models.CharField(max_length=100)

	def __str__(self):
		""" Return the name of the driver """
		return str(self.name)

class Bus(models.Model):
	name = models.CharField(max_length=100)
	cost = models.IntegerField(null=True, blank=True)
	prom_package_price = models.IntegerField(null=True, blank=True)
	active = models.BooleanField()
	description = models.CharField(max_length=500, null=True, blank=True)
	primary_image = models.ImageField(null=True, blank=True)
	secondary_image = models.ImageField(null=True, blank=True)
	affiliate = models.ForeignKey(Affiliate, blank=True, null=True)

	def __str__(self):
		""" Return the name of the bus """
		return str(self.name)

	class Meta:
		ordering = ['name']
		verbose_name = 'Bus'
		verbose_name_plural = 'Buses'

class Customer(models.Model):
	first_name = models.CharField(max_length=100, default='new')
	last_name = models.CharField(max_length=100, null=True, blank=True)
	phone_number = models.CharField(max_length=12, null=True, blank=True)
	email = models.CharField(max_length=100, null=True, blank=True)
	comments = models.CharField(max_length=1024, null=True, blank=True)
	stripe_customer_id = models.CharField(max_length=30, blank=True, null=True)

	def __str__(self):
		""" Return the id of the model """
		fn = self.first_name.title()
		ln = self.last_name.title()
		name = fn + " " + ln
		return str(name)

# Create your models here.
class Reservation(models.Model):
	""" User entry reservation data. This is a one to one ralationship. 
	other models will relate to this model using a UUID Primary key."""

	STATUS_NEW = 'n'
	STATUS_PENDING = 'p'
	STATUS_COMPLETED = 'c'

	# ^-- to access choice model attributes easier.
	# ex. -> Reservation.objects.filter(status=Reservation.STATUS_NEW)

	reservation_status_choices = {
	(STATUS_NEW,'new'),
	(STATUS_PENDING, 'pending'),
	(STATUS_COMPLETED, 'completed'),
	}

	id = models.UUIDField(primary_key=True,
		default=uuid.uuid4, editable=False)
	bus = models.ForeignKey(
		Bus, blank=True, null=True)
	customer = models.ForeignKey(Customer, null=True, blank=True,)
	date = models.DateField()
	start_time = models.TimeField(default="16:00", null=True, blank=True)
	duration = models.IntegerField("Number of hours")
	location_pick_up = models.CharField(max_length=1024, null=True, blank=True)
	location_drop_off= models.CharField(max_length=1024, null=True, blank=True)
	comments = models.CharField(max_length=1024, null=True, blank=True)
	created = models.DateTimeField(null=True, blank=True)
	email = models.EmailField()
	driver = models.ForeignKey(Driver, blank=True, null=True)
	status = models.CharField(max_length=100, choices=reservation_status_choices,
		null=True, blank=True)
	total_price = models.IntegerField(default=0)

	def __str__(self):
		""" Return the id of the model """
		return str(self.id)

	def get_price(self, reservation):
		""" calculate the price and savings amount and save it to
		total_price and quote_savings respectively. Use the bus
		cost to get the quote amount. """

		min_hours = 4
		transport_charge = 1.15
		tax_charge = 1.0725

		# Get variables from reservation instance and bus object

		duration = reservation.duration
		date = reservation.date
		day_of_week = date.weekday()
		bus_cost = reservation.bus.cost 
		

		transport_charge = 0.20 # Standard service fee
		tax_rate_charge = 0.0725 # County sales tax rate

		# Friday and Saturday pricing
		#if day_of_week in [4, 5]:
		#	bus_cost += 10

		price = bus_cost * duration * 100 * \
		(1 + transport_charge) * (1 + tax_rate_charge)

		reservation.total_price = price 

		from .high_demand import prom_season_dates

		if date in prom_season_dates:
			reservation.total_price = reservation.bus.prom_package_price * 100
			reservation.duration = 6

		reservation.save()


class Charge(models.Model):
	""" Store and process all data from stripe processed payments 
	by reservation. """
	TYPE_DEPOSIT = 'deposit'
	TYPE_COMPLETE = 'full payment'
	TYPE_OTHER = 'other'

	charge_type_choices = {
		(TYPE_DEPOSIT, 'deposit'),
		(TYPE_COMPLETE, 'complete'),
		(TYPE_OTHER, 'other'),
		}

	stripe_id = models.CharField(max_length=30, blank=True)
	reservation = models.ForeignKey(Reservation, blank=True, null=True)
	customer = models.ForeignKey(Customer)
	amount = models.IntegerField()
	description = models.CharField(max_length=200, blank=True)
	charge_type = models.CharField(max_length=30, choices=charge_type_choices,
		null=True, blank=True)

	def __str__(self):
		""" Return the id of the model """
		return str(self.stripe_id)

class Comment(models.Model):
	reservation = models.ForeignKey(Reservation, blank=True, null=True)
	author = models.CharField(max_length=100)
	text = models.TextField()
	created_date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.text

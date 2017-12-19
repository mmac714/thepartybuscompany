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

#from .reservation_num_generator import reservation_num_generator


bus_sizes = (
	('12', '12 passengers'),
	('16', '16 passengers'),
	('22', '22 passengers'),
	('30', '30 passengers'),
	)

no_res_survey_choices = {
	('service', "I'm not sure if you offer the service I'm looking for"),
	('prices too high', "Party buses are too expensive"),
	('prices not competitive', "I found a lower price somewhere else"),
	('bus',"I want more info on the bus"),
	('quotes',"I'm just here to get a quote"),
}

# Create your models here.
class Reservation(models.Model):
	"""User entry reservation data.
	This is a one to many rationship. 
	Detail and payment will relate to this model."""
	id = models.UUIDField(primary_key=True,
		default=uuid.uuid4, editable=False)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	bus_size = models.CharField(max_length=2,choices=bus_sizes)
	date = models.DateField()
	start_time = models.TimeField(default="19:00", null=True, blank=True)
	duration = models.IntegerField("Number of hours")
	location_pick_up = models.CharField(max_length=1024, null=True, blank=True)
	location_drop_off= models.CharField(max_length=1024, null=True, blank=True)
	comments = models.CharField(max_length=1024, null=True, blank=True)
	quote_amount = models.IntegerField(default=0)
	phone_number = models.CharField(max_length=12)
	created = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		""" Return the id of the model """
		return str(self.id)

	def derive_quote_amount(self, reservation):
		""" Calculate and store the payment amount. """
		duration = reservation.duration
		bus_size = reservation.bus_size
		date = reservation.date
		day_of_week = date.weekday()
		added_hours = duration - 4

		if bus_size == "30":
			base_price = 520
			added_hour_price = 120
		elif bus_size == "22":
			base_price = 480
			added_hour_price = 110
		elif bus_size == "16":
			base_price = 440
			added_hour_price = 105
		elif bus_size == "12":
			base_price = 400
			added_hour_price = 95

		# Friday and Saturday pricing
		if day_of_week in [4, 5]:
			base_price += 40
			added_hour_price += 10

		# promotional offer 
		if bus_size == "12" and day_of_week in [0,1,2,3]:
			base_price = 320
			added_hour_price = 80

		reservation.quote_amount = (base_price + (added_hours * added_hour_price))*100
		reservation.quote_amount = reservation.quote_amount*1.2
		reservation.quote_amount = reservation.quote_amount*1.0725
		reservation.save()

	def create_payment_instance(self, reservation):
		Payment.objects.create(reservation=reservation)
		NoResSurvey.objects.create(reservation=reservation)
		#time stamp creation
		reservation.created = timezone.now()

class SurveyManager(models.Manager):
	def get_queryset(self):
		return super(SurveyManager, self).get_queryset().exclude(reason='None')

class NoResSurvey(models.Model):
	reservation = models.OneToOneField(Reservation,
		primary_key=True,
		)
	reason = models.CharField(max_length=150, choices=no_res_survey_choices,
		null=True, blank=True)
	detail = models.TextField(null=True, blank=True, max_length=300)
	surveyed = SurveyManager()
	objects = models.Manager()

	def __str__(self):
		""" Return the id of the model """
		return str(self.reservation_id)



class Payment(models.Model):

	reservation = models.OneToOneField(Reservation,
		primary_key=True,
		)
	email = models.EmailField()
	stripe_id = models.CharField(max_length=30, blank=True)
	charge_amount = models.IntegerField(default=0)
	charge_status = models.CharField(max_length=100, blank=True)
	charge_description = models.CharField(max_length=200, blank=True)
	stripe_customer_id = models.CharField(max_length=30, blank=True)

	def __str__(self):
		""" Return the id of the model """
		return str(self.reservation_id)

	def store_stripe_customer_in_db(self, reservation_instance, 
		customer_instance):
		""" takes the reservation number to store the stripe
		customer id and email. """
		res = reservation_instance
		customer = customer_instance

		# store variables
		res.stripe_customer_id = customer.id
		res.email = customer.email

		res.save()


	def create_stripe_customer(self, token, email, reservation):
		""" Creates a stripe customer.
		Saves the card on file.
		Save the customer's id and email to the database."""
		reservation = Payment(str(reservation))

		try:
			customer = stripe.Customer.create(
				source=token,
				email=email,
				)

		except stripe.error.CustomerError as ce:
			return ce

		else:
			Payment().store_stripe_customer_in_db(reservation, customer)

	def store_stripe_payment_in_db(self, reservation_instance, 
		charge_instance, customer_instance):
		""" store stripe objects to the payment instance """
		res = reservation_instance
		charge = charge_instance
		customer = customer_instance

		res.stripe_id = charge.id
		res.charge_amount = charge.amount
		res.charge_status = charge.outcome.type
		res.charge_description = charge.description

		res.stripe_customer_id = customer.id
		res.email = customer.email

		res.save()

	def create_and_charge_customer(self, token, email, reservation):
		""" Creates a new customer and charges their card for
		the reservation. """
		fee = reservation.quote_amount
		bus_size = reservation.bus_size
		reservation = Payment(str(reservation))

		try:
			customer = stripe.Customer.create(
				source=token,
				email=email,
				)

		except Exception as ce:
			return ce

		stripe_customer_id = customer.id

		try:
			charge = stripe.Charge.create(
				amount=20000,
				currency="usd",
				customer=stripe_customer_id,
				description=bus_size,
				)

		except stripe.error.CardError as ce:
			# Errors will only happen on fraud cards
			err = ce.json_body.get('error', {})
			new_payment.charge_status = err.get('type')
			new_payment.charge_desription = err.get('message')
			new_payment.save()
			return False

		else:
			Payment().store_stripe_payment_in_db(reservation, charge, customer)


	def send_booking_confirmation_email(self, email, reservation):
		"""send email to confirm reservation and payment. """
		payment = Payment.objects.get(reservation=reservation)
		email = [str(email),]
		fee = str(int(payment.charge_amount)/100)
		fee = "$" + fee + "0"
		charge_description = payment.charge_description
		reservation_date = reservation.date
		
		# set additional variables
		today = datetime.date.today()
		subject = 'Thanks for booking with us!'
		body = get_template('bookings/confirmation_email.html').render(
			{
			'email': email,
			'fee': fee,
			'today':today, 
			'charge_description':charge_description,
			'reservation_date':reservation_date,
			})
		sender = 'service@ThePartyBusCompany.io'
		recipient = email

		send_mail(subject, "", sender, recipient, html_message=body, fail_silently=False)

		#send to service email address
		recipient = ['service@ThePartyBusCompany.io']
		subject = 'New Reservation ' + str(reservation.date)
		send_mail(subject, "", sender, recipient, html_message=body, fail_silently=False)



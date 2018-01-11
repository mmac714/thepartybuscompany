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

# bus sizes offered
bus_sizes = (
	('12', '12 passengers'),
	('16', '16 passengers'),
	('22', '22 passengers'),
	('30', '30 passengers'),
	)

# Survey choice
no_res_survey_choices = {
	('service', "I'm not sure if you offer the service I'm looking for"),
	('prices too high', "Party buses are too expensive"),
	('prices not competitive', "I found a lower price somewhere else"),
	('bus',"I want more info on the bus"),
	('quotes',"I'm just here to get a quote"),
}

# reservation status 
reservation_status_choices = {
	('new','new'),
	('pending', 'pending'),
	('completed', 'completed'),
}

# reservation status 
payment_status_choices = {
	('no deposit', 'no deposit'),
	('paid deposit', 'paid deposit'),
	('completed', 'completed'),
}

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'bus_{0}/{1}'.format(instance.slug, filename)

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
	active = models.BooleanField()
	description = models.CharField(max_length=500, null=True, blank=True)
	#primary_image = models.ImageField(null=True, blank=True)
	#secondary_image = models.ImageField(null=True, blank=True)
	affiliate = models.ForeignKey(Affiliate, blank=True, null=True)

	def __str__(self):
		""" Return the name of the bus """
		return str(self.name)


# Constant reservation model variables
min_hours = 4
transport_charge = 1.15
tax_charge = 1.0725

# Create your models here.
class Reservation(models.Model):
	""" User entry reservation data. This is a one to one ralationship. 
	other models will relate to this model using a UUID Primary key."""
	id = models.UUIDField(primary_key=True,
		default=uuid.uuid4, editable=False)
	bus = models.ForeignKey(
		Bus, blank=True, null=True)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	date = models.DateField()
	start_time = models.TimeField(default="4:00 PM", null=True, blank=True)
	duration = models.IntegerField("Number of hours")
	location_pick_up = models.CharField(max_length=1024, null=True, blank=True)
	location_drop_off= models.CharField(max_length=1024, null=True, blank=True)
	comments = models.CharField(max_length=1024, null=True, blank=True)
	quote_amount = models.IntegerField(default=0)
	phone_number = models.CharField(max_length=12)
	created = models.DateTimeField(null=True, blank=True)
	quote_savings = models.IntegerField(null=True, blank=True)
	email = models.EmailField()
	driver = models.ForeignKey(Driver, blank=True, null=True)
	status = models.CharField(max_length=100, choices=reservation_status_choices,
		null=True, blank=True)

	def __str__(self):
		""" Return the id of the model """
		return str(self.id)

	def get_price(self, reservation):
		""" calculate the price and savings amount and save it to
		quote_amount and quote_savings respectively. Use the bus
		cost to get the quote amount. """

		# Get variables from reservation instance and bus object

		duration = reservation.duration
		date = reservation.date
		day_of_week = date.weekday()
		bus_cost = reservation.bus.cost 
		

		transport_charge = 0.25 # Standard service fee
		tax_rate_charge = 0.0725 # County sales tax rate

		# Friday and Saturday pricing
		if day_of_week in [4, 5]:
			bus_cost += 10

		price = bus_cost * duration * 100 * \
		(1 + transport_charge) * (1 + tax_rate_charge)

		reservation.quote_amount = price 

		reservation.save()

	def calculate_decayed_price(self, base_price, added_hour_price, 
		duration, date):
		""" Derive a discounted price depending on how far out the 
		customer is reserving. The max discount is at 60 days, and 
		reservations made within 3 days of the reservation date will not
		be discounted. """
		added_hours = duration - min_hours
		today = datetime.date.today()
		day_delta = date - today
		day_delta = day_delta.days

		if day_delta > 60: #Discount stops at 60 days
			day_delta = 60

		if day_delta > 3: # Within three days is considered day of rate
			daily_rate_decay = .1
		else:
			daily_rate_decay = 0

		# Derive early reservation discount for the base rate
		base_price_decayed = ((base_price / min_hours) 
			- (daily_rate_decay * day_delta)) * min_hours

		# Derive early reservation discount for hours over the base rate
		add_hourly_price_decayed = (added_hour_price 
			- (daily_rate_decay * day_delta)) * added_hours

		# calculate total discounted price
		# 100 is for stripe conversion pricing
		total_price = base_price_decayed + add_hourly_price_decayed
		total_price = total_price * transport_charge * tax_charge * 100

		return total_price

	def get_demand_fee(self, date):
		""" Determine the demand fee by counting the amount
		of reservation objects created for that date not including 
		quotes created today. """

		# get dates and convert them to query readable strings.
		today = datetime.datetime.today().strftime('%Y-%m-%d')
		date = date.strftime('%Y-%m-%d')

		# Retrieve reservation objects that have a reservation date
		# equal to the instance's reservation date.
		# Remove objects that were created today.
		# Count the remaining objects.
		reservations = Reservation.objects.all()
		
		query_date_count = \
		reservations.filter(date=date).exclude(created__contains=today).count()

		# Demand fee increase by 58 cents, which is the average cost 
		# per click on google as of 12/21/2017 divided by 3 (arbitrary)
		demand_fee = query_date_count * 58

		return demand_fee

	def derive_quote_amount(self, reservation):
		""" Calculate and store the payment amount. """
		duration = reservation.duration
		bus_size = reservation.bus_size
		date = reservation.date
		day_of_week = date.weekday()

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

		added_hours = duration - min_hours

		# derive price if reserved on the reservation date
		zero_day_price = (base_price + (added_hours * added_hour_price))*100
		zero_day_price = zero_day_price * (transport_charge + 0.05) # 20% fee
		zero_day_price = zero_day_price * tax_charge

		reservation.quote_amount = \
		Reservation().calculate_decayed_price(base_price, added_hour_price, 
			duration, date) # + Reservation().get_demand_fee(date)

		reservation.quote_savings = zero_day_price - reservation.quote_amount \
		+ 522 # + Reservation().get_demand_fee(date) # taking into account 3 google ad cost at 1.74 avg

		# promotional offer 
		if bus_size == "12" and day_of_week in [0,1,2,3]:
			base_price = 320
			added_hour_price = 80

			reservation.quote_amount = (base_price + (added_hours * added_hour_price))*100
			reservation.quote_amount = reservation.quote_amount*1.2
			reservation.quote_amount = reservation.quote_amount*1.0725

		reservation.save()

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
	status = models.CharField(max_length=100, choices=payment_status_choices,
		null=True, blank=True)

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
		res.status = "paid deposit"

		res.save()

	def create_and_charge_customer(self, token, email, reservation):
		""" Creates a new customer and charges their card for
		the reservation. """
		fee = reservation.quote_amount
		bus = reservation.bus
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
				description=bus,
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



from django.shortcuts import render, get_object_or_404, \
redirect, HttpResponseRedirect, reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.db.models import Q
from django.db import IntegrityError

import stripe
import datetime, time

from .forms import ReservationForm, BackendReservationForm, BookingResForm,\
ContactForm, QuoteForm, NoResSurveyForm, PriceForm, CreateBusForm, \
CreateDriverForm, CreateAffiliateForm, EditBusForm

from .models import Reservation, Payment, NoResSurvey, SurveyManager, Bus,\
Driver, Affiliate

from pb_config.settings import STRIPE_SECRET_KEY, STRIPE_PUBLIC_KEY

stripe.api_key = STRIPE_SECRET_KEY
stripe_api_key = STRIPE_PUBLIC_KEY

# Static pages
def prices(request):
	return render(request, 'bookings/prices.html')

def specials(request):
	return render(request, 'bookings/specials.html')

def highdemand(request):
	return render(request, 'bookings/highdemand.html')

def more_than_sixty_days(request):
	return render(request, 'bookings/more_than_sixty_days.html')

def contact(request):
	return render(request, 'bookings/contact.html')

def faq(request):
	return render(request, 'bookings/faq.html')

# Non static pages
def home(request):
	""" Contact form email logic.
	List bus objects with links to create a new reservation with 
	the selected bus. """

	if request.method == 'POST':
		form = ContactForm(request.POST)

		if form.is_valid():
			email = request.POST.get("from_email")
			customer_email = [str(email),]

			try:
				sender = 'service@ThePartyBusCompany.io'
				recipient = customer_email
				message = form.cleaned_data['message']
				body = get_template('bookings/web_message_confirmation.html').render(
					{'message': message,
					})
				# Send email to customer
				send_mail('The Party Bus Company',"", sender, recipient,
					html_message=body, fail_silently=False)
				# Send email to service
				recipient = ['service@ThePartyBusCompany.io']
				subject = 'Web Contact - ' + str(customer_email)

				send_mail(subject, "", email, recipient, html_message=body,
					fail_silently=False)

			except BadHeaderError:
				return HttpResponse('Invalid header found.')

			return HttpResponseRedirect(reverse('bookings:contact'))

	# Display only acitve buses
	buses = Bus.objects.filter(active=True)

	form = ContactForm()

	context = {
		'buses':buses,
		'form':form,
		}
	return render(request, 'bookings/home.html', context)

def get_bus_and_create_reservation(request, bus_id):
	""" Called when the customer selects a bus from the home page. 
	This function will take the bus.id from the link and create a 
	new reservation model with default setting and pass the reservation
	to the price form."""
	
	# Retrieve the bus id from the link
	bus = Bus.objects.get(id=bus_id)

	today = datetime.date.today()
	saturday = today + datetime.timedelta( (12 - today.weekday()) % 7)

	# Create a reservation model with the bus_id and default values
	reservation = Reservation.objects.create(
		date=saturday,
		duration=4,
		bus_id=bus.id,
		created=timezone.now()
		)

	# send reservation id to price form
	return HttpResponseRedirect(reverse('bookings:price_form',
					args=[reservation.id]))


def price_form(request, reservation_id):
	""" customer is displayed the price form to complete. Once submitted,
	the form data will be saved to the reservation instance, a payment 
	object will be created, a price will be calculated and the customer
	will be directed to the appropriate page depending on their input. """

	reservation = Reservation.objects.get(id=reservation_id)

	if request.method == 'POST':
		# Form was submitted
		form = PriceForm(request.POST, instance=reservation)
		if form.is_valid():
			# Form fields passed validation.
			form.save()

			# create payment object for the reservation instance
			# can't create payment object here, maybe create it in the 
			# reservation view

			# Calculate price
			Reservation().get_price(reservation)

			from .high_demand import high_demand_list

			# Variables for redirect logic
			res_date = reservation.date
			today = datetime.date.today()
			day_delta = res_date - today

			# send to high demand page if the date is in the
			# High demand list
			if res_date in high_demand_list:
				return HttpResponseRedirect(reverse('bookings:highdemand'))
			
			# Send to high demand if the customer wants to book within
			# 2 days
			elif day_delta < datetime.timedelta(2):
				return HttpResponseRedirect(reverse('bookings:highdemand'))

			# Only give quotes and allow reservations if 
			# within 60 days of the reservation date.
			elif day_delta > datetime.timedelta(60):
				return HttpResponseRedirect(reverse(
					'bookings:more_than_sixty_days'))

			# In good order - give customer the price
			else:	
				return HttpResponseRedirect(reverse('bookings:quote',
					args=[reservation]))
	else:
		form = PriceForm(instance=reservation)

	context = {
	'reservation': reservation,
	'form': form,
	}

	return render(request, 'bookings/price_form.html', context)

def quote(request, reservation_id):
	reservation = Reservation.objects.get(id=reservation_id)
	bus = reservation.bus

	context = {
	'reservation': reservation,
	'bus': bus,
	}

	return render(request, 'bookings/quote.html', context)

# Create your views here.
def reservation_form(request, reservation_id):
	reservation = Reservation.objects.get(id=reservation_id)
	""" Form for the customer to complete their booking details. """
	if request.method == 'POST':
		# Form was submitted
		form = ReservationForm(request.POST, instance=reservation)
		form.date = reservation.date
		if form.is_valid():
			# Form fields passed validation.
			form.save()

			# Create Payment object
			# Try block to avoid creating a duplicate payment object
			# if one already exist for the reservation. This may happen
			# if the customer submits the form and goes back to edit
			# the form and resubmit it. 
			try:
				Payment.objects.create(reservation=reservation)
			except IntegrityError:
				pass

			return HttpResponseRedirect(reverse('bookings:payment',
					args=[reservation]))
		else:
			return HttpResponse(form.errors.as_data())
	else:
		form = ReservationForm(instance=reservation)

		context = {
			'form': form,
			'reservation': reservation
			}
		return render(request, 'bookings/reservation_form.html', context)

# Not using this right now
def quote_no_reservation(request, reservation_id):
	reservation = Reservation.objects.get(id=reservation_id)
	survey = NoResSurvey.objects.get(reservation=reservation_id)


	if request.method == 'POST':
		form = NoResSurveyForm(request.POST, instance=survey)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('bookings:home'))

	else:
		form = NoResSurveyForm()
		
		context = {
		'reservation': reservation,
		'form': form,
		}

		return render(request, 'bookings/quote_no_reservation.html', context)


@csrf_exempt #cannot pass CSRF cookie to stripe and back
def payment(request, reservation_id):
	""" User's reservation data, agreement, payment. """
	reservation = Reservation.objects.get(id=reservation_id)
	payment = Payment.objects.get(reservation=reservation_id)
	context = {
		'reservation': reservation,
		'payment': payment,
		'stripe_api_key':stripe_api_key,
		}
	sent = False

	if request.method == "POST":
		# Payment form submitted. Process payment.

		# Retrieve token and email from form.
		token = request.POST.get("stripeToken")
		email = request.POST.get("stripeEmail")
		
		Payment().create_and_charge_customer(token, email, reservation)
		Payment().send_booking_confirmation_email(email, reservation)
		sent = True

		return HttpResponseRedirect(reverse('bookings:confirmation',
			args=[reservation_id]))

	return render(request, 'bookings/payment.html', context)


def confirmation(request, reservation_id):
	""" Respond with booking confirmation data. """
	reservation = Reservation.objects.get(id=reservation_id)


	context = {
		'reservation': reservation
		}
	return render(request, 'bookings/confirmation.html', context)

@login_required
def booking(request, reservation_id):
	""" Page for associate to fill out Reservation detail. """
	reservation = Reservation.objects.get(id=reservation_id)
	payment = Payment.objects.get(reservation=reservation_id)
	#bus = Bus.objects.get(reservation=reservation_id)

	if request.method == 'POST' and 'btn-r_form':
		r_form = BookingResForm(request.POST, instance=reservation)
		if r_form.is_valid():
			r_form.save()

			return HttpResponseRedirect(reverse('bookings:booking',
				args=[reservation_id]))

	#if request.method == 'POST' and 'invoice':
	#	invoice = (request.POST, instance=detail)
		#d_form = DetailForm(request.POST, instance=detail)

	#	return HttpResponseRedirect(reverse('bookings:invoice',
	#		args=[reservation_id]))

	else:
		r_form = BookingResForm(initial={
			'date': reservation.date,
			'duration': reservation.duration,
			'quote_amount': reservation.quote_amount,
			'bus': reservation.bus,
			})

		context = {
    		'reservation': reservation,
    		'r_form': r_form,
    		'payment': payment,
    		}

		return render(request, 'bookings/booking.html', context)

@login_required
def send_follow_up_email(request, reservation_id):
	""" Sends followup_quote_email.html to the 
	reservation.email address. """
	reservation = Reservation.objects.get(id=reservation_id)
	customer_email = [str(reservation.email),]

	price = str(int(reservation.quote_amount)/100)
	price = "$" + price + "0"
	bus = reservation.bus.name
	date = reservation.date
	date = date.strftime('%m/%d')
	duration = reservation.duration
	quote_link = "www.ThePartyBusCompany.io/quote/" + str(reservation.id) + \
	"/"

	# Email arguments
	subject = "Your event on " + str(date) + " with The " + str(bus) + "."
	body = get_template('bookings/followup_quote_email.html').render(
		{
		'price': price,
		'date': date,
		'bus': bus,
		'quote_link': quote_link,
		})
	sender = 'service@ThePartyBusCompany.io'
	recipient = customer_email


	send_mail(subject, "", sender, recipient,
		html_message=body,
		fail_silently=False)

	return HttpResponse("email sent")


@login_required
def invoice(request, reservation_id):
	""" Page for associate to fill out Reservation detail. """
	reservation = Reservation.objects.get(id=reservation_id)
	payment = Payment.objects.get(reservation=reservation_id)

	context = {
    	'reservation': reservation,
    	'payment': payment
    	}

	return render(request, 'bookings/invoice.html', context)

@login_required
def booking_list(request):
	""" Show all bookings. """
	bookings = Reservation.objects.order_by('-created').exclude(created__isnull=True)
	payment = Payment()

	context = {	
		'bookings': bookings,
		'payment': payment,
		}
	return render(request, 'bookings/booking_list.html', context)


@login_required
def completed_reservation_list(request):
	""" Show all completed reservations. """
	reservations = Reservation.objects.order_by('-date').filter(
		payment__charge_status='authorized')
	payment = Payment()

	context = {	
		'reservations': reservations,
		'payment': payment,
		}
	return render(request, 'bookings/completed_reservation_list.html', context)




@login_required
def survey_list(request):
	""" Show all submitted surveys. """
	surveys = NoResSurvey.objects.all().filter(
		Q(reason='prices not competitive')|\
		Q(reason='service')|\
		Q(reason='prices too high')|\
		Q(reason='bus')|\
		Q(reason='quotes'))

	context = {	
		'surveys': surveys,
		}
	return render(request, 'bookings/survey_list.html', context)

def sitemap(request):

	return HttpResponse(
		open('bookings/static/Bookings/sitemap.xml').read(),
		content_type='text/xml')

def favicon(request):

	return HttpResponse(
		open('bookings/static/Bookings/img/logo.png').read(),
		content_type='image/png')

@login_required
def backend_reservation(request):
	""" Show the reservation form and add a new reservation"""
	if request.method == 'POST':
		# Form was submitted
		form = BackendReservationForm(request.POST)
		if form.is_valid():
			# Form fields passed validation.
			form.save()
			reservation = form.save()
			reservation.created=timezone.now()
			reservation.save()
			# clean data?
			try:
				Payment.objects.create(reservation=reservation)
			except IntegrityError:
				pass

			return HttpResponseRedirect(reverse('bookings:payment',
					args=[reservation]))
				# Send to relevant payment.html
	else:
		form = BackendReservationForm()

	context = {
		'form': form,
		}
	return render(request, 'bookings/backend-reservation.html', context)



@login_required
def vehicle_management(request):
	""" Allow uses to create buses. """
	form = CreateBusForm()
	buses = Bus.objects.all()


	if request.method == 'POST':
		form = CreateBusForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('bookings:vehicle_management'))


	context = {
		'form': form,
		'buses': buses,
		}
	return render(request, 'bookings/vehicle_management.html', context)

@login_required
def driver_management(request):
	""" Allow users to create drivers and see all drivers. """
	form = CreateDriverForm()
	drivers = Driver.objects.all()

	if request.method == 'POST':
		form = CreateDriverForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('bookings:driver_management'))


	context = {
		'form': form,
		'drivers': drivers,
		}
	return render(request, 'bookings/driver_management.html', context)

@login_required
def affiliate_management(request):
	""" Allow users to create and see all affiliates. """
	form = CreateAffiliateForm()
	affiliates = Affiliate.objects.all()

	if request.method == 'POST':
		form = CreateAffiliateForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('bookings:affiliate_management'))

	context = {
		'form': form,
		'affiliates': affiliates,
	}

	return render(request, 'bookings/affiliate_management.html', context)


@login_required
def vehicle_profile(request, vehicle_id):
	""" Allow users to edit and see vehicle information """
	vehicle = Bus.objects.get(id=vehicle_id)

	if request.method == 'POST':
		form = EditBusForm(request.POST, instance=vehicle)
		if form.is_valid():
			form.save()

			return HttpResponseRedirect(reverse('bookings:vehicle_management'))

	form = EditBusForm(
		initial={
		'cost': vehicle.cost, 
		'active':vehicle.active,
		'description': vehicle.description,
		'affiliate': vehicle.affiliate,
		})

	context = {
	'vehicle': vehicle,
	'form': form,
	}

	return render(request, 'bookings/vehicle_profile.html', context)












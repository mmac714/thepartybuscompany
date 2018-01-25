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
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, Http404

import stripe
import datetime, time

from .forms import ReservationForm, BackendReservationForm, BookingResForm,\
ContactForm, QuoteForm, NoResSurveyForm, PriceForm, CreateBusForm, \
CreateDriverForm, CreateAffiliateForm, EditBusForm, EditAffiliateForm, \
EditDriverForm, PriceCalculatorForm, CommentForm

from .models import Reservation, Payment, NoResSurvey, SurveyManager, Bus,\
Driver, Affiliate, Comment

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

def under_construction(request):
	return render(request, 'bookings/under_construction.html')

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
	# Create Payment object
			# Try block to avoid creating a duplicate payment object
			# if one already exist for the reservation. This may happen
			# if the customer submits the form and goes back to edit
			# the form and resubmit it. 
	try:
		Payment.objects.create(reservation=reservation,status="no deposit")
	except IntegrityError:
		pass


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
			#elif day_delta > datetime.timedelta(60):
			#	return HttpResponseRedirect(reverse(
			#		'bookings:more_than_sixty_days'))

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
	comments = Comment.objects.filter(reservation=reservation)

	if request.method == 'POST' and 'btn-r_form':
		r_form = BookingResForm(request.POST, instance=reservation)
		if r_form.is_valid():
			r_form.save()

			return HttpResponseRedirect(reverse('bookings:booking',
				args=[reservation_id]))

	if request.method == 'POST' and 'CommentForm':
		comment_form = CommentForm(request.POST)
		if comment_form.is_valid():
			comment = comment_form.save(commit=False)
			comment.reservation = reservation
			comment.author = request.user.first_name + " " + \
			request.user.last_name
			comment_form.save()

			return HttpResponseRedirect(reverse('bookings:booking',
				args=[reservation_id]))

	r_form = BookingResForm(initial={
		'date': reservation.date,
		'duration': reservation.duration,
		'quote_amount': reservation.quote_amount,
		'bus': reservation.bus,
		'driver': reservation.driver,
		'location_pick_up': reservation.location_pick_up,
		'location_drop_off': reservation.location_drop_off,
		'comments': reservation.comments,

		})

	comment_form = CommentForm()
	

	context = {
    	'reservation': reservation,
    	'r_form': r_form,
    	'payment': payment,
    	'comment_form':comment_form,
    	'comments':comments,
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
	quote_link = "https://www.ThePartyBusCompany.io/quote/" + str(reservation.id) + \
	"/"

	# Email arguments
	subject = "Your event on " + str(date) + " with the " + str(bus) + "."
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

def customer_agreement(request):
	try:
		return FileResponse(open(
			'bookings/static/Bookings/CustomerServiceAgreement.pdf', 'rb'), 
			content_type='application/pdf')
	except FileNotFoundError:
		raise Http404()

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
				Payment.objects.create(reservation=reservation,
					status="no deposit")
			except IntegrityError:
				pass

			return HttpResponseRedirect(reverse('bookings:booking',
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
	""" Allow uses to create buses and see all buses. """
	form = CreateBusForm()
	buses = Bus.objects.all()

	if request.method == 'POST':
		form = CreateBusForm(request.POST, request.FILES)
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
	""" Allow users to create and see all drivers. """
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
	vehicle_reservations = vehicle.reservation_set.order_by('-date')

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
	'vehicle_reservations': vehicle_reservations
	}

	return render(request, 'bookings/vehicle_profile.html', context)

@login_required
def affiliate_profile(request, affiliate_id):
	""" Allow users to edit and see affiliate information """
	affiliate = Affiliate.objects.get(id=affiliate_id)
	affiliate_vehicles = affiliate.bus_set.all()

	if request.method == 'POST':
		form = EditAffiliateForm(request.POST, instance=affiliate)
		if form.is_valid():
			form.save()

			return HttpResponseRedirect(reverse('bookings:affiliate_management'))

	form = EditAffiliateForm(
		initial = {
		'contact': affiliate.contact,
		})

	context = {
	'affiliate': affiliate,
	'form': form,
	'affiliate_vehicles': affiliate_vehicles,
	}

	return render(request, 'bookings/affiliate_profile.html', context)

@login_required
def driver_profile(request, driver_id):
	""" Allow users to edit and see driver information """
	driver = Driver.objects.get(id=driver_id)
	driver_reservations = driver.reservation_set.order_by('-date')

	if request.method == 'POST':
		form = EditDriverForm(request.POST, instance=driver)
		if form.is_valid():
			form.save()

			return HttpResponseRedirect(reverse('bookings:driver_management'))

	form = EditDriverForm(
		initial = {
		'contact': driver.contact,
		})

	context = {
	'driver': driver,
	'form': form,
	'driver_reservations': driver_reservations,
	}

	return render(request, 'bookings/driver_profile.html', context)

@login_required
def payment_no_deposit_list(request):
	""" Show newly created reservations with no deposits. """
	reservations = Reservation.objects.order_by('-date').filter(
		payment__status='no deposit')
	payment = Payment()

	context = {
		'reservations':reservations,
		'payment': payment,
	}

	return render(request, 'bookings/payment_no_deposit_list.html', context)

@login_required
def payment_paid_deposit_list(request):
	""" Show newly created reservations with no deposits. """
	reservations = Reservation.objects.order_by('-date').filter(
		payment__status='paid deposit')
	payment = Payment()

	context = {
		'reservations':reservations,
		'payment': payment,
	}

	return render(request, 'bookings/payment_paid_deposit_list.html', context)

@login_required
def payment_completed_list(request):
	""" Show newly created reservations with no deposits. """
	reservations = Reservation.objects.order_by('-date').filter(
		payment__status='completed')
	payment = Payment()

	context = {
		'reservations':reservations,
		'payment': payment,
	}

	return render(request, 'bookings/payment_completed_list.html', context)

@login_required
def reservations_upcoming_list(request):
	""" show upcoming reservations. """
	today = datetime.date.today()
	next_seven_days = datetime.date.today() + datetime.timedelta(7)
	reservations = Reservation.objects.order_by('date').filter(
		date__range=(today,next_seven_days))

	context = {
		'reservations': reservations,
	}

	return render(request, 'bookings/reservations_upcoming_list.html', context)

@login_required
def price_calculator_form(request):
	""" Get form data to calculate a price and P/L """

	if request.method == 'POST':
		hourly_rate = int(request.POST.get("hourly_rate_cost"))

		hours = int(request.POST.get("hours"))

		hourly_markup = int(request.POST.get("hourly_markup"))
		service_fee_rate = float(request.POST.get("service_fee_rate"))/100
		tax_rate = 0.0725
		cc_fee_rate = 0.029
		cc_flat_charge_fee = 0.30



		total_charge_amount = ((hourly_rate + hourly_markup) * hours) *\
		(1 + service_fee_rate) * (1 + tax_rate)

		total_cost = (hourly_rate * hours) + \
		(total_charge_amount * cc_fee_rate) + cc_flat_charge_fee \
		+ (total_charge_amount * tax_rate)

		return HttpResponse(
			"Price: {}".format(round(total_charge_amount, 2)) +
			"    " +
			"Total cost: {}".format(round(total_cost, 2)) +
			"    " +
			"Profit: {}".format(round(round(total_charge_amount, 2) - \
			round(total_cost, 2),2))

			)

	form = PriceCalculatorForm()

	context = {
	'form':form
	}

	return render(request, 'bookings/price_calculator_form.html', context)

@login_required 
def add_comment_to_post(request, reservation_id):
	reservation = get_object_or_404(Reservation, id=reservation_id)

	if request.method == "POST":
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.reservation = reservation
			reservation.save()
			return redirect('bookings:booking', id=reservation_id)

	else:
		form = CommentForm()

	context = {
	'form':form
	}

	return render(request, 'bookings/booking.html', context)

@login_required
def send_deposit_link_email(request, reservation_id):
	""" Send deposit_link_email.html to the reservation.email address.
	The purpose of this email to give the customer a direct link to
	pay their deposit to complete their booking. """

	reservation = Reservation.objects.get(id=reservation_id)
	customer_email = [str(reservation.email),]
	customer_name = reservation.first_name
	customer_name = customer_name.title()

	date = reservation.date
	date = date.strftime('%m/%d')

	payment_link = "https://www.ThePartyBusCompany.io/payment/" + str(reservation.id) + \
	"/"

	# Email arguments
	subject = "Complete Your Party Bus Reservation - " + str(date) 
	body = get_template('bookings/deposit_link_email.html').render(
		{
		'date': date,
		'payment_link': payment_link,
		'customer_name': customer_name,
		})
	sender = 'service@ThePartyBusCompany.io'
	recipient = customer_email


	send_mail(subject, "", sender, recipient,
		html_message=body,
		fail_silently=False)

	return HttpResponse("email sent")
































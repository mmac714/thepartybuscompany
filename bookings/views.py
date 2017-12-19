from django.shortcuts import render, get_object_or_404, \
redirect, HttpResponseRedirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.db.models import Q

import stripe

from .forms import ReservationForm, BackendReservationForm, BookingResForm,\
ContactForm, QuoteForm, NoResSurveyForm

from .models import Reservation, Payment, NoResSurvey, SurveyManager

from pb_config.settings import STRIPE_SECRET_KEY, STRIPE_PUBLIC_KEY

stripe.api_key = STRIPE_SECRET_KEY
stripe_api_key = STRIPE_PUBLIC_KEY

# Static pages
def prices(request):
	return render(request, 'bookings/prices.html')

def buses(request):
	return render(request, 'bookings/buses.html')

def specials(request):
	return render(request, 'bookings/specials.html')

def highdemand(request):
	return render(request, 'bookings/highdemand.html')

def contact(request):
	return render(request, 'bookings/contact.html')

# Non static pages
def home(request):
	form = ContactForm()

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

	context = {
		'form': form,
		}
	return render(request, 'bookings/home.html', context)


# Create your views here.
def reservation(request, reservation_id):
	reservation = Reservation.objects.get(id=reservation_id)
	""" Show the reservation form and add a new reservation"""
	if request.method == 'POST':
		# Form was submitted
		form = ReservationForm(request.POST, instance=reservation)
		form.date = reservation.date
		if form.is_valid():
			# Form fields passed validation.
			form.save()
			# clean data?
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
		return render(request, 'bookings/reservation.html', context)

def quote_form(request):
	""" Show the Initial quote form, and calculate quote """
	if request.method == 'POST':
		# Form was submitted
		form = QuoteForm(request.POST)
		if form.is_valid():
			# Form fields passed validation.
			form.save()
			new_reservation = form.save()
			Reservation().create_payment_instance(new_reservation)
			Reservation().derive_quote_amount(new_reservation)

			# Send to high demand page if date in high demand list
			reservation = Reservation.objects.get(id=new_reservation.id)
			from .high_demand import high_demand_list

			if reservation.date in high_demand_list:
				return HttpResponseRedirect(reverse('bookings:highdemand'))
			else:	
				return HttpResponseRedirect(reverse('bookings:quote',
					args=[new_reservation]))
					# Send to relevant payment.html

	else:
		form = QuoteForm()

	context = {
		'form': form,
		}
	return render(request, 'bookings/quote_form.html', context)

def quote(request, reservation_id):
	reservation = Reservation.objects.get(id=reservation_id)

	context = {
	'reservation': reservation,
	}

	return render(request, 'bookings/quote.html', context)

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
			})

		context = {
    		'reservation': reservation,
    		'r_form': r_form,
    		'payment': payment,
    		}

		return render(request, 'bookings/booking.html', context)

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
	bookings = Reservation.objects.order_by('created').exclude(first_name='')
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
			new_reservation = form.save()
			# clean data?
			Reservation().create_payment_instance(new_reservation)
			return HttpResponseRedirect(reverse('bookings:payment',
				args=[new_reservation.id]))
				# Send to relevant payment.html
	else:
		form = BackendReservationForm()

	context = {
		'form': form,
		}
	return render(request, 'bookings/backend-reservation.html', context)






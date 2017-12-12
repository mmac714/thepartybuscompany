from django.shortcuts import render, get_object_or_404, \
redirect, HttpResponseRedirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context

import stripe

from .forms import ReservationForm, BackendReservationForm, BookingResForm
from .models import Reservation, Payment

from pb_config.settings import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY

# Static pages
def home(request):
	return render(request, 'bookings/home.html')

def prices(request):
	return render(request, 'bookings/prices.html')

def buses(request):
	return render(request, 'bookings/buses.html')

def specials(request):
	return render(request, 'bookings/specials.html')

def highdemand(request):
	return render(request, 'bookings/highdemand.html')

# Create your views here.
def reservation(request):
	""" Show the reservation form and add a new reservation"""
	if request.method == 'POST':
		# Form was submitted
		form = ReservationForm(request.POST)
		if form.is_valid():
			# Form fields passed validation.
			form.save()
			new_reservation = form.save()
			# clean data?
			Reservation().create_payment_instance(new_reservation)
			Reservation().derive_quote_amount(new_reservation)
			
			# Send to high demand page if date in high demand list
			reservation = Reservation.objects.get(id=new_reservation.id)
			from .high_demand import high_demand_list

			if reservation.date in high_demand_list:
				return HttpResponseRedirect(reverse('bookings:highdemand'))
			else:	
				return HttpResponseRedirect(reverse('bookings:payment',
					args=[new_reservation.id]))
					# Send to relevant payment.html
	else:
		form = ReservationForm()

	context = {
		'form': form,
		}
	return render(request, 'bookings/reservation.html', context)


@csrf_exempt #cannot pass CSRF cookie to stripe and back
def payment(request, reservation_id):
	""" User's reservation data, agreement, payment. """
	reservation = Reservation.objects.get(id=reservation_id)
	payment = Payment.objects.get(reservation=reservation_id)
	context = {
		'reservation': reservation,
		'payment': payment,
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
	bookings = Reservation.objects.order_by('date')
	payment = Payment()

	context = {	
		'bookings': bookings,
		'payment': payment,
		}
	return render(request, 'bookings/booking_list.html', context)

def sitemap(request):

	return HttpResponse(
		open('bookings/static/PartyBus/sitemap.xml').read(),
		content_type='text/xml')


# Create your views here.
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






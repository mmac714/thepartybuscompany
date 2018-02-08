""" Prices """







""" Stripe functions """
import stripe
stripe.api_key = STRIPE_SECRET_KEY

def stripe_create_customer_and_store_payment_token(token, email):
		""" Creates a stripe customer. Stores the stripe customer's ID
		to the Customer instnace. """
		try: 
			customer = stripe.Customer.create(
				source=token, # payment token for charges
				email=email,
				)

		except stripe.error.CustomerError as ce:
			return ce

def create_and_store_charge_on_db(customer, reservation, charge_type, charge):
	""" store payment data to the db when the customer has been charged. """
	try:
		Charge.objects.create(
			customer = customer,
			reservation = reservation,
			charge_type = charge_type,
			stripe_id = charge.id,
			amount = charge.amount,
			description = charge.charge_description
			)
	except IntegrityError:
		pass


def stripe_charge_customer(amount, customer, reservation, charge_type, description):
		""" A generic charge function that can be used to charge
		the deposit, full amount, or other amount. This will use the 
		stripe customer API object to charge the customer,
		not the card. """

		# Amount can be anything
		charge = stripe.Charge.create(
			amount=amount,
			currency="usd",
			customer=customer, # Customer.stripe_customer_id
			description=description
			)

		create_and_store_charge_on_db(customer, reservation, charge_type, charge)





""" Email functions """
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


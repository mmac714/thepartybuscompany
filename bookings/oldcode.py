class Payment(models.Model):
	""" Store and process all data from stripe processed payments 
	by reservation. """

	STATUS_NONE = 'none'
	STATUS_DEPOSIT = 'depost'
	STATUS_PAID = 'paid'

	payment_status_choices = {
		(STATUS_NONE, 'no deposit'),
		(STATUS_DEPOSIT, 'paid deposit'),
		(STATUS_PAID, 'completed'),
		}

	reservation = models.OneToOneField(Reservation,
		primary_key=True,
		)
	stripe_id = models.CharField(max_length=30, blank=True)
	charge_amount = models.IntegerField(default=0)
	charge_status = models.CharField(max_length=100, blank=True)
	charge_description = models.CharField(max_length=200, blank=True)
	status = models.CharField(max_length=100, choices=payment_status_choices,
		null=True, blank=True)
	customer = models.ForeignKey(
		Customer, blank=True, null=True)

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
		""" Creates a new stripe customer and charges their card for
		the reservation. """
		fee = reservation.quote_amount
		bus = reservation.bus
		reservation = Payment(str(reservation))

		try:
			customer = stripe.Customer.create(
				source=token,
				email=email,
				)

			# Save stripe id to customer model here?

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

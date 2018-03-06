from django.utils import timezone

import datetime

today = datetime.date.today()
saturday = today + datetime.timedelta( (12 - today.weekday()) % 7)

def get_next_saturday():
	""" Returns next Saturday in datetime format. """
	today = datetime.date.today()
	saturday = today + datetime.timedelta( (12 - today.weekday()) % 7)

	return saturday

def get_time_stamp():
	return timezone.now()


""" Email functions """
from django.template.loader import get_template
from django.core.mail import send_mail, BadHeaderError

def send_contact_form_email(recipient, message):
	try:
		sender = 'service@ThePartyBusCompany.io'
		email_template = 'bookings/web_message_confirmation.html'
		body = get_template(email_template).render(
			{'message': message,})

		# Send email to customer
		send_mail('The Party Bus Company',"", sender, recipient,
			html_message=body, fail_silently=False)
		# Send email to service
		recipient = ['service@ThePartyBusCompany.io']
		subject = 'Web Contact - ' + str(recipient)

		send_mail(subject, "", sender, recipient, html_message=body,
			fail_silently=False)

	except BadHeaderError:
		return HttpResponse('Invalid header found.')
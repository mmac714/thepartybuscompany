from django.test import TestCase, Client
from django.urls import resolve, reverse
from django.core import mail
from django.forms import EmailField

from importlib import import_module

from ...models import Reservation, Bus
from ...views import home, select_bus_link
from ...helper_functions import get_next_saturday, get_time_stamp,\
send_contact_form_email
from ...forms import ContactForm

class HomeTest(TestCase):
	def setUp(self):
		url = reverse('bookings:home')
		self.response = self.client.get(url)
		self.recipient = 'john@doe.com'
		self.message = 'testing123'
		self.form_data = {'from_email': self.recipient, 'message': self.message}
		self.form = ContactForm(data=self.form_data)

	def test_vaild_form(self):
		self.assertTrue(self.form.is_valid())

	def test_invalid_form(self):
		self.form_data['message'] = ''
		form = ContactForm(data=self.form_data)
		self.assertFalse(form.is_valid())

	def test_individual_form_fields(self):
		self.assertFieldOutput(EmailField, 
			{'a@a.com': 'a@a.com'}, 
			{'aaa': ['Enter a valid email address.']})

	def test_form_errors(self):
		field = 'from_email'
		self.form_data[field] = ''
		form = ContactForm(data=self.form_data)
		error_text = 'This field is required.'
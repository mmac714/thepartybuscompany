from django.test import TestCase, Client
from django.forms import EmailField
from django.urls import reverse

import datetime
yesterday = datetime.date.today() - datetime.timedelta(1)

from ...forms import PriceForm
from ...helper_functions import get_next_saturday

class PriceFormTest(TestCase):
	def setUp(self):
		self.form_data = {
			'date': get_next_saturday(), 
			'duration': 4,
			'email': 'john@doe.com',
			}
		self.form = PriceForm(data=self.form_data)
		#url = reverse('bookings:price_form')
		#self.response = self.client.get(url)

	def test_valid_form(self):
		self.assertTrue(self.form.is_valid())

	def test_invalid_form(self):
		form_data = {
			'date': '', 
			}
		self.form = PriceForm(data=form_data)
		self.assertFalse(self.form.is_valid())

	def test_date_before_today(self):
		self.form_data = {
			'date': yesterday, 
			'duration': 4,
			'email': 'john@doe.com',
			}
		error = 'The reservation date is before today.'
		#self.assertFormError(self.response, 'form', 'date', error)

































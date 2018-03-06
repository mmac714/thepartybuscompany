from django.test import TestCase, Client
from django.urls import resolve, reverse
from django.core import mail
from django.forms import EmailField

from importlib import import_module

from ..models import Reservation, Bus
from ..views import home, select_bus_link
from ..helper_functions import get_next_saturday, get_time_stamp,\
send_contact_form_email
from ..forms import ContactForm

class HomeViewTestCase(TestCase):
	def setUp(self):
		# Create buses to test context and session varaible
		for i in range(5):
			self.bus = Bus.objects.create(
				name='TestBus' + str(i),
				active=True,
				cost = 100
				)

		self.bus = Bus.objects.create(
				name='TestBusFalse' + str(i),
				active=False,
				cost = 100
				)

		# variables to test response and session
		self.url = reverse('bookings:home')

class HomeViewTests(HomeViewTestCase):
	def setUp(self):
		super().setUp()
		self.response = self.client.get(self.url)
		self.session = self.client.session
		self.first_bus = Bus.objects.all().get(name='TestBus0')

	def test_form_fail(self):
		form = ContactForm()
		self.fail(form.as_p())


	def test_status_code(self):
		self.assertEquals(self.response.status_code, 200)

	def test_view_function(self):
		view = resolve('/')
		self.assertEquals(view.func, home)

	def test_home_view_template(self):
		self.assertTemplateUsed(self.response, 'bookings/home.html')

	def test_home_view_context(self):
		# Only show active buses
		self.assertEqual(len(self.response.context['buses']), 5)
		self.assertIsInstance(self.response.context['form'], ContactForm)

	def test_session_variable_in_home_view(self):
		self.session['bus'] = self.first_bus
		self.assertEqual(self.session.get('bus').name, 'TestBus0')

	def test_home_view_contains_unbound_form(self):
		form = self.response.context.get('form')
		self.assertIsInstance(form, ContactForm)
		self.assertFalse(form.is_bound)

	def test_form_inputs(self):
		""" View must containt two inputs:
		Email, Message and CSRF. CSRF and Email can be identified 
		via input, the message is a text area widget and can be 
		identified as such. """
		self.assertContains(self.response, '<input', 2)
		self.assertContains(self.response, 'type="email"', 1)
		self.assertContains(self.response, '<textarea', 1)
		self.assertContains(self.response, 'csrfmiddlewaretoken', 1)

class SuccessfulHomeViewPostRequest(HomeViewTestCase):
	def setUp(self):
		super().setUp()
		self.recipient = 'john@doe.com'
		self.message = 'lorem ipsum'
		self.response = self.client.post(self.url,
			{'from_email': self.recipient, 'message': self.message})

	def test_form_is_bound(self):
		form = self.response.context.get('form')
		self.assertTrue(form.is_bound)

	def test_send_contact_email(self):
		recipient_list = [self.recipient,]
		# Verify that 2 emails are sent
		self.assertEqual(len(mail.outbox), 2)
		# Verify that the subject, sender and recipient of the email.
		self.assertEqual(mail.outbox[0].subject, 'The Party Bus Company')
		self.assertEqual(mail.outbox[1].from_email, 
			'service@ThePartyBusCompany.io')
		self.assertEqual(mail.outbox[0].to, recipient_list) #returns list

	def test_redirection(self):
		contact_url = reverse('bookings:contact')
		self.assertRedirects(self.response, contact_url)

class InvalidHomeViewPostRequest(HomeViewTestCase):
	def setUp(self):
		super().setUp()
		self.response = self.client.post(self.url,
			{})

	def test_status_code(self):
		""" An invalid form submission should return the same page. """
		self.assertEqual(self.response.status_code, 200)

	def test_form_errors(self):
		form = self.response.context.get('form')
		#self.assertTrue(form.is_bound)
		#self.assertTrue(form.errors)


































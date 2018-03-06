from django.test import TestCase
from django.urls import resolve, reverse

from ..models import Reservation, Bus
from ..views import home, select_bus_link
from ..helper_functions import get_next_saturday, get_time_stamp

class GetBusAndCreateReservationTestCase(TestCase):
	def setUp(self):
		self.bus = Bus.objects.create(
			name='TestBus',
			active=True,
			cost = 100
			)

		self.reservation = Reservation.objects.create(
			date=get_next_saturday(),
			duration=4,
			bus=self.bus,
			)
		self.url = reverse('bookings:price_form', 
			kwargs={'reservation_id': self.reservation.pk }
			)
		

class HomeTest(GetBusAndCreateReservationTestCase):

	def setUp(self):
		super().setUp()
		self.response = self.client.get(self.url)

	def test_home_view_status_code(self):
		self.assertEquals(self.response.status_code, 200)

	def test_home_url_resolves_home_view(self):
		view = resolve('/')
		self.assertEquals(view.func, home)
from django import forms
from .models import Reservation
from django.contrib.admin import widgets   

import datetime

from bootstrap_datepicker.widgets import DatePicker


from pb_config.settings import DATE_INPUT_FORMATS

# find the next saturday for date initial value
today = datetime.date.today()
saturday = today + datetime.timedelta( (5-today.weekday()) % 7)


class ReservationForm(forms.ModelForm):


	date = forms.DateField(initial=saturday, widget=DatePicker(
		options={
			"format": "mm/dd/yyyy",
			"autoclose": True,
		}))
	duration = forms.IntegerField(widget=forms.NumberInput, initial=3, min_value=3, label='# of hours')

	class Meta:
		model = Reservation
		fields = [
		'first_name', 
		'last_name', 
		'bus_size',
		'date',
		'start_time',
		'duration',
		'location_pick_up',
		'location_drop_off',
		'comments',
		] 
		labels = {
			'first_name': 'First Name',
			'last_name': 'Last Name',
			'bus_size': 'Group Size',
			'date': 'Reservation Date',
			'start_time': 'Start Time',
			'duration': 'Number of Hours',
			'location_pick_up': 'Pick Up Location',
			'location_drop_off': 'Drop Off Location',
			'comments': 'Service Comments or Request',
			}



class BackendReservationForm(forms.ModelForm):
	#p 2404
	date = forms.DateField(initial=saturday, widget=DatePicker(
		options={
			"format": "mm/dd/yyyy",
			"autoclose": True,
		}))
	duration = forms.IntegerField(widget=forms.NumberInput, initial=3, min_value=3, label='# of hours')
	class Meta:
		model = Reservation
		fields = [
		'first_name', 
		'last_name', 
		'bus_size',
		'date',
		'start_time',
		'duration',
		'location_pick_up',
		'location_drop_off',
		'comments',
		'quote_amount',
		] 
		labels = {
			'first_name': 'First Name',
			'last_name': 'Last Name',
			'bus_size': 'Group Size',
			'date': 'Reservation Date',
			'start_time': 'Start Time',
			'duration': 'Number of Hours',
			'location_pick_up': 'Pick Up Location',
			'location_drop_off': 'Drop Off Location',
			'comments': 'Service Comments or Request',
			'quote_amount': 'Total Cost Amount',
			}

class BookingResForm(forms.ModelForm):
	""" list all reservation objects """
	class Meta:
		model = Reservation
		fields = ['date','duration', 'quote_amount' ] 











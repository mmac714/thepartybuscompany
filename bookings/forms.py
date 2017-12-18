from django import forms
from .models import Reservation, NoResSurvey
from django.contrib.admin import widgets   

import datetime

from bootstrap_datepicker.widgets import DatePicker


from pb_config.settings import DATE_INPUT_FORMATS

# find the next saturday for date initial value
today = datetime.date.today()
saturday = today + datetime.timedelta( (5-today.weekday()) % 7)

class QuoteForm(forms.ModelForm):
	date = forms.DateField(initial=saturday, widget=DatePicker(
		options={
			"format": "mm/dd/yyyy",
			"autoclose": True,
		}))
	duration = forms.IntegerField(widget=forms.NumberInput, initial=5, min_value=4,
		max_value=12, label='Number of hours')

	class Meta:
		model = Reservation
		fields = [
		'date',
		'bus_size',
		'duration'
			]

		labels = {
		'date':'Reservation Date',
		'bus_size':'Group Size',
		'duration': 'Number of hours',
			}

class ReservationForm(forms.ModelForm):

	#def write_quoteform_date_to_form

	date = forms.DateField(initial=saturday, widget=DatePicker(
		options={
			"format": "mm/dd/yyyy",
			"autoclose": True,
		}))

	duration = forms.IntegerField(widget=forms.NumberInput, initial=5, min_value=4,
		max_value=12, label='Number of hours')

	class Meta:
		model = Reservation
		fields = [
		'first_name', 
		'last_name', 
		'phone_number',
		'start_time',
		'location_pick_up',
		'location_drop_off',
		'comments',
		'date',
		'duration',
		] 
		labels = {
			'first_name': 'First Name',
			'last_name': 'Last Name',
			'phone_number': 'Phone Number',
			'bus_size': 'Group Size',
			'start_time': 'Start Time',
			'location_pick_up': 'Pick Up Location',
			'location_drop_off': 'Drop Off Location',
			'comments': 'Service Comments or Request',
			'duration': 'Number of Hours',
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
		'phone_number',
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
			'phone_number': 'Phone Number',
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

class ContactForm(forms.Form):
	from_email = forms.EmailField(required=True, label='Your email address')
	message = forms.CharField(widget=forms.Textarea, required=True)

class NoResSurveyForm(forms.ModelForm):
	""" form to take a survey of why people did not want reserve. """
	class Meta:
		model = NoResSurvey
		fields = ['reason', 'detail']
		labels = {
			'detail': 'Open feedback (optional)',
			}












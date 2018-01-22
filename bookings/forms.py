from django import forms
from django.contrib.admin import widgets
from django.core.exceptions import ValidationError

import datetime

from bootstrap_datepicker.widgets import DatePicker

from .models import Reservation, NoResSurvey, Bus, Driver, Affiliate,\
Comment
from pb_config.settings import DATE_INPUT_FORMATS

# find the next saturday for date initial value
today = datetime.date.today()
saturday = today + datetime.timedelta( (12 - today.weekday()) % 7)

class QuoteForm(forms.ModelForm):
	date = forms.DateField(initial=saturday, widget=DatePicker(
		options=
		{
			"format": "mm/dd/yyyy",
			"autoclose": True,
		}))
	duration = forms.IntegerField(widget=forms.NumberInput, initial=4, min_value=4,
		max_value=12, label='Number of hours')

	# extend date validation
	def clean_date(self):
		date = self.cleaned_data['date']
		# Don't allow before today
		if date < today:
			raise forms.ValidationError("\
				The reservation date is before today.")
		return date

	class Meta:
		model = Reservation
		fields = [
		'date',
		'duration',
		'email',
		'bus',
			]

		labels = {
		'date':'Reservation Date',
		'duration': 'Number of hours',
		'email': 'Your email',
			}

class PriceForm(forms.ModelForm):
	
	date = forms.DateField(initial=saturday, widget=forms.SelectDateWidget(
		empty_label=('year_label', 'month_label', 'day_label')))
	"""
	date = forms.DateField(initial=saturday, widget=DatePicker(
		attrs={
		'class': 'datepicker datepicker-inline'},
		options=
		{
			"format": "mm/dd/yyyy",
			"autoclose": True,
		}))
	"""
	duration = forms.IntegerField(widget=forms.NumberInput, initial=4, min_value=4,
		max_value=12, label='Number of hours')

	# extend date validation
	def clean_date(self):
		date = self.cleaned_data['date']
		# Don't allow before today
		if date < today:
			raise forms.ValidationError("\
				The reservation date is before today.")
		return date

	class Meta:
		model = Reservation
		fields = [
		'date',
		'duration',
		'email',
			]

		labels = {
		'date':'Reservation Date',
		'duration': 'Number of hours',
		'email': 'Your email',
			}

class ReservationForm(forms.ModelForm):

	#def write_quoteform_date_to_form
	"""
	date = forms.DateField(initial=saturday, widget=DatePicker(
		options={
			"format": "mm/dd/yyyy",
			"autoclose": True,
		}))

	duration = forms.IntegerField(widget=forms.NumberInput, initial=5, min_value=4,
		max_value=12, label='Number of hours')
	"""

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
		] 
		labels = {
			'first_name': 'First Name',
			'last_name': 'Last Name',
			'phone_number': 'Phone Number',
			'start_time': 'Start Time',
			'location_pick_up': 'Pick Up Location (optional)',
			'location_drop_off': 'Drop Off Location (optional)',
			'comments': 'Service Comments or Request (optional)',
			}



class BackendReservationForm(forms.ModelForm):
	#p 2404

	date = forms.DateField(initial=saturday, widget=forms.SelectDateWidget(
		empty_label="nothing"))

	#date = forms.DateField(initial=saturday, widget=DatePicker(
	#	options={
	#		"format": "mm/dd/yyyy",
	#		"autoclose": True,
	#	}))
	duration = forms.IntegerField(widget=forms.NumberInput, initial=4, min_value=3, label='# of hours')
	start_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'), initial="4:00 PM")
	
	class Meta:
		model = Reservation
		fields = [
		'first_name', 
		'last_name', 
		'phone_number',
		'date',
		'start_time',
		'duration',
		'location_pick_up',
		'location_drop_off',
		'comments',
		'quote_amount',
		'bus',
		'email'
		] 
		labels = {
			'first_name': 'First Name',
			'last_name': 'Last Name',
			'phone_number': 'Phone Number',
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
		fields = ['date','duration', 'quote_amount','bus', 'driver' ] 

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

class CreateBusForm(forms.ModelForm):
	class Meta:
		model = Bus
		fields = ['name', 'cost', 'active', 
		'primary_image', 'secondary_image',
		'description', 'affiliate']

class EditBusForm(forms.ModelForm):
	class Meta:
		model = Bus
		fields = ['cost', 'active', 'description', 'affiliate']

class CreateDriverForm(forms.ModelForm):
	class Meta:
		model = Driver
		fields = ['name', 'contact']

class EditDriverForm(forms.ModelForm):
	class Meta:
		model = Driver
		fields = ['contact']


class CreateAffiliateForm(forms.ModelForm):
	class Meta:
		model = Affiliate
		fields = ['name', 'contact']

class EditAffiliateForm(forms.ModelForm):
	class Meta:
		model = Affiliate
		fields = ['contact']

class PriceCalculatorForm(forms.Form):
	hourly_rate_cost = forms.IntegerField()
	hours = forms.IntegerField()
	hourly_markup = forms.IntegerField()
	service_fee_rate = forms.IntegerField()


class CommentForm(forms.ModelForm):

	class Meta:
		model = Comment
		fields = ['text']


		









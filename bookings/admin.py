from django.contrib import admin

# Register your models here.
from .models import Reservation, Payment, NoResSurvey, Bus, Affiliate, Driver

admin.site.register(Reservation)
admin.site.register(Payment)
admin.site.register(NoResSurvey)
admin.site.register(Bus)
admin.site.register(Affiliate)
admin.site.register(Driver)
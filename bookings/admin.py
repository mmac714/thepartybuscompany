from django.contrib import admin

# Register your models here.
from .models import Reservation, Bus, Charge, Customer,\
Affiliate, Driver, Comment

admin.site.register(Reservation)
admin.site.register(Charge)
admin.site.register(Bus)
admin.site.register(Affiliate)
admin.site.register(Driver)
admin.site.register(Customer)
admin.site.register(Comment)
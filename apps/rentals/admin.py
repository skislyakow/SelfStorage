from django.contrib import admin

from .models import RentalOrder, DeliveryRequest

admin.site.register(RentalOrder)
admin.site.register(DeliveryRequest)

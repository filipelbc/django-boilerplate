from django.contrib import admin

from .models import Customer, Device, Reading


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer')
    list_select_related = ('customer', )


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ('id', 'device', 'customer', 'timestamp', 'reading')
    list_select_related = ('device', 'device__customer')

    def customer(self, obj):
        return obj.device.customer

from django.contrib import admin
from django.contrib import auth
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

# Register your models here.
from mpesa_api.models import StkPushCalls


class StkPushCallsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    list_display = (
        'id', 'businessShortCode', 'txnId', 'accountReference', 'amount', 'phoneNumber', 'merchantRequestId',
        'checkoutRequestId', 'stkStatus', 'paymentStatus', 'statusReason')


admin.site.register(StkPushCalls, StkPushCallsAdmin)

admin.site.unregister(User)
admin.site.unregister(Group)

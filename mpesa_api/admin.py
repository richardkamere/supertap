from django.contrib import admin

# Register your models here.
from mpesa_api.models import StkPushCalls

class StkPushCallsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'businessShortCode', 'txnId', 'accountReference', 'amount', 'phoneNumber', 'merchantRequestId',
        'checkoutRequestId',
        'responseCode', 'stkStatus', 'paymentStatus','statusReason')


# admin.site.register(MpesaPayment)

# admin.site.register(MpesaCallBacks)

# admin.site.register(MpesaCalls)

admin.site.register(StkPushCalls, StkPushCallsAdmin)

import json

import requests
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class StkPushCalls(BaseModel):
    businessShortCode = models.CharField(max_length=255)
    transactionType = models.CharField(max_length=225)
    amount = models.IntegerField()
    partyA = models.CharField(max_length=225)
    partyB = models.CharField(max_length=255)
    phoneNumber = models.CharField(max_length=255)
    accountReference = models.CharField(max_length=255)
    transactionDesc = models.CharField(max_length=255)
    merchantRequestId = models.CharField(max_length=255)
    checkoutRequestId = models.CharField(max_length=255)
    responseCode = models.CharField(max_length=255)
    responseDescription = models.CharField(max_length=255)
    customerMessage = models.CharField(max_length=255)
    stkStatus = models.CharField(max_length=255, default="Success")
    paymentStatus = models.CharField(max_length=255, default="Pending")
    statusReason = models.CharField(max_length=255, default="not know")



# M-pesa Payment models
class MpesaCalls(BaseModel):
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()

    class Meta:
        verbose_name = 'Mpesa Call'
        verbose_name_plural = 'Mpesa Calls'


class MpesaCallBacks(BaseModel):
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()

    class Meta:
        verbose_name = 'Mpesa Call Back'
        verbose_name_plural = 'Mpesa Call Backs'


class MpesaPayment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.0)
    mpesaReceiptNumber = models.CharField(max_length=100, blank=True)
    transactionDate = models.IntegerField(blank=True)
    phoneNumber = models.CharField(max_length=100,blank=True)

    class Meta:
        verbose_name = 'Mpesa Payment'
        verbose_name_plural = 'Mpesa Payments'

    def __str__(self):
        return self.amount

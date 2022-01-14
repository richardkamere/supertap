import json
from enum import Enum

import requests
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class StkPushCalls(BaseModel):
    businessShortCode = models.CharField(max_length=255, verbose_name="Short Code")
    transactionType = models.CharField(max_length=225)
    amount = models.DecimalField(max_digits=30, default=0.00, decimal_places=2)
    partyA = models.CharField(max_length=225)
    partyB = models.CharField(max_length=255)
    phoneNumber = models.CharField(max_length=255, verbose_name="Phone Number")
    accountReference = models.CharField(max_length=255, verbose_name="Paid Account")
    transactionDesc = models.CharField(max_length=255)
    merchantRequestId = models.CharField(max_length=255)
    checkoutRequestId = models.CharField(max_length=255)
    responseCode = models.CharField(max_length=255)
    responseDescription = models.CharField(max_length=255)
    customerMessage = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255, null=True, verbose_name="First Name")
    last_name = models.CharField(max_length=255, null=True, verbose_name="Last Name")
    middle_name = models.CharField(max_length=255, null=True, verbose_name="Middle Name")
    firebase_token = models.CharField(max_length=255, null=True)
    stkStatus = models.CharField(max_length=255, default="Failed", verbose_name="STK Status")
    paymentStatus = models.CharField(max_length=255, default="Pending", verbose_name="Payment Status")
    statusReason = models.CharField(max_length=255, default="not know", verbose_name="Status Reason")
    txnId = models.CharField(max_length=255, default="1212", verbose_name="Txn Id")
    txnRefNo = models.CharField(max_length=255, null=True, verbose_name="Mpesa TxnId")
    transactionDate = models.DateTimeField(auto_now=True)
    retryTimes = models.IntegerField(default=0, verbose_name="STK Retries")

    class Meta:
        verbose_name_plural = "STK PAYMENTS"
        verbose_name = "transaction"


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
    phoneNumber = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Mpesa Payment'
        verbose_name_plural = 'Mpesa Payments'

    def __str__(self):
        return self.amount

import json

import requests
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import renderers
from requests.auth import HTTPBasicAuth
from rest_framework import viewsets
from rest_framework.decorators import permission_classes, api_view, renderer_classes
from rest_framework.permissions import AllowAny

from mpesa_api.serializers import UserSerializer

User = get_user_model()
from mpesa_api.models import StkPushCalls
from mpesa_api.mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword, MpesaC2bCredential


@csrf_exempt
def getAccessToken(request):
    consumer_key = MpesaC2bCredential.consumer_key
    consumer_secret = MpesaC2bCredential.consumer_secret
    api_URL = MpesaC2bCredential.access_token_url;
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']
    return HttpResponse(validated_mpesa_access_token)


@csrf_exempt
def auto_check_payment(request):
    checkRequest = json.loads(request.body)
    print(checkRequest)

    try:
        data = StkPushCalls.objects.filter(txnId=checkRequest['txnId']).order_by('-id')[0]
        if data.paymentStatus == "Success":
            context = {
                "stkStatus": data.stkStatus,
                "customerMessage": data.customerMessage,
                "paymentStatus": data.paymentStatus,
                "statusReason": data.statusReason,
                "txnRefNo": data.txnRefNo,
                "customerName": data.customerName,
                "phoneNumber": data.phoneNumber,
                "paidAmount": data.amount
            }
            return JsonResponse(dict(context))
        else:
            # access_token = MpesaAccessToken.validated_mpesa_access_token
            # api_url = MpesaC2bCredential.check_payment_status_url
            # headers = {"Authorization": "Bearer %s" % access_token}

            # request = {
            #     "CommandID": LipanaMpesaPpassword.customerBuyGoodsOnline,
            #     "Amount": data.amount,
            #     "Msisdn": data.phoneNumber,
            #     "ShortCode": data.businessShortCode
            # }
            #
            # response = requests.post(api_url, json=request, headers=headers)
            #
            # print(response.text)

            context = {
                "stkStatus": data.stkStatus,
                "customerMessage": data.customerMessage,
                "paymentStatus": data.paymentStatus,
                "statusReason": data.statusReason,
                "txnRefNo": data.txnRefNo,
                "customerName": data.first_name,
                "phoneNumber": data.phoneNumber,
                "paidAmount": data.amount
            }
            return JsonResponse(dict(context))

    except ObjectDoesNotExist:
        context = {
            "stkStatus": "Stk Not Received",
            "customerMessage": "Stk Not Received, Please Tap Again",
            "paymentStatus": "Failed",
            "statusReason": "Stk Not Received, Request the customer to Tap Again",
            "txnRefNo": "Nil",
            "customerName": "John Doe",
            "phoneNumber": "0700 0000000",
            "paidAmount": "0.00"
        }
        return JsonResponse(dict(context))


@csrf_exempt
def lipa_na_mpesa_online(request):
    stkRequest = json.loads(request.body)
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = MpesaC2bCredential.stk_push_url
    headers = {"Authorization": "Bearer %s" % access_token}

    request = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": stkRequest['amount'],
        "PartyA": stkRequest['phoneNumber'],  # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPpassword.Business_short_code,
        "PhoneNumber": stkRequest['phoneNumber'],  # replace with your phone number to get stk push
        "CallBackURL": MpesaC2bCredential.stk_push_callback_url,
        "AccountReference": stkRequest['merchantName'],
        "TransactionDesc": "PESAPAL SABI"
    }

    # check if the transaction exists
    if not StkPushCalls.objects.filter(txnId=stkRequest['txnId'], paymentStatus="Success").exists():
        response = requests.post(api_url, json=request, headers=headers)

        if response.status_code == 200:
            stkRequestV1 = StkPushCalls(
                businessShortCode=request['BusinessShortCode'],
                transactionType=request['TransactionType'],
                amount=request['Amount'],
                partyA=request['PartyA'],
                partyB=request['PartyB'],
                phoneNumber=request['PhoneNumber'],
                accountReference=request['AccountReference'],
                transactionDesc=request['TransactionDesc'],
                merchantRequestId=response.json()['MerchantRequestID'],
                checkoutRequestId=response.json()['CheckoutRequestID'],
                responseCode=response.json()['ResponseCode'],
                responseDescription=response.json()['ResponseDescription'],
                customerMessage=response.json()['CustomerMessage'],
                stkStatus="Success",
                paymentStatus="Pending",
                statusReason="Stk sent, Waiting for customer to complete payment",
                txnId=stkRequest['txnId']
            )

            if not StkPushCalls.objects.filter(txnId=stkRequest['txnId']).exists():
                stkRequestV1.save()
            else:
                originalCall = StkPushCalls.objects.filter(txnId=stkRequest['txnId']).order_by('-id')[0]
                originalCall.checkoutRequestId = response.json()['CheckoutRequestID']
                originalCall.merchantRequestId = response.json()['CheckoutRequestID']
                originalCall.retryTimes = originalCall.retryTimes + 1
                originalCall.save()
                print("updated")

            context = {
                "ResponseCode": response.json()['ResponseCode'],
                "CustomerMessage": response.json()['CustomerMessage']
            }

            return JsonResponse(dict(context))

        else:
            stkRequestV1 = StkPushCalls(
                businessShortCode=request['BusinessShortCode'],
                transactionType=request['TransactionType'],
                amount=request['Amount'],
                partyA=request['PartyA'],
                partyB=request['PartyB'],
                phoneNumber=request['PhoneNumber'],
                accountReference=request['AccountReference'],
                transactionDesc=request['TransactionDesc'],
                merchantRequestId=response.json()['requestId'],
                checkoutRequestId=response.json()['requestId'],
                responseCode=response.json()['errorCode'],
                responseDescription=response.json()['errorMessage'],
                customerMessage=response.json()['errorMessage'],
                stkStatus="Failed",
                paymentStatus='Failed',
                statusReason=response.json()['errorMessage'],
                txnId=stkRequest['txnId']
            )

            if not StkPushCalls.objects.filter(txnId=stkRequest['txnId'], paymentStatus="Success").exists():
                stkRequestV1.save()

            context = {
                "ResponseCode": 1,
                "CustomerMessage": response.json()['errorMessage']
            }

            return JsonResponse(dict(context))

    else:
        context = {
            "ResponseCode": 1,
            "CustomerMessage": "Transaction complete, Please Tap your phone on the terminal again"
        }
        return JsonResponse(dict(context))


@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    print(MpesaC2bCredential.api_URL)
    print(access_token)

    api_url = MpesaC2bCredential.register_url
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPpassword.Test_c2b_shortcode,
               "ResponseType": "Completed",
               "ConfirmationURL": MpesaC2bCredential.confirmation_url,
               "ValidationURL": MpesaC2bCredential.validation_url
               }
    response = requests.post(api_url, json=options, headers=headers)
    return HttpResponse(response.text)


@csrf_exempt
def call_back(request):
    pass


@csrf_exempt
def validation(request):
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    print(" validation received ...")
    return JsonResponse(dict(context))


@csrf_exempt
def c2b_confirmation(request):
    mpesa_body = request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)

    if not StkPushCalls.objects.filter(phoneNumber=mpesa_payment['MSISDN'], amount=mpesa_payment['TransAmount'],
                                       businessShortCode=mpesa_payment['BusinessShortCode'],
                                       paymentStatus="Success").order_by('-id')[0].exist():
        originalCall = \
            StkPushCalls.objects.filter(phoneNumber=mpesa_payment['MSISDN'], amount=mpesa_payment['TransAmount'],
                                        businessShortCode=mpesa_payment['BusinessShortCode'],
                                        paymentStatus="Success").order_by('-id')[0];

        originalCall.first_name = mpesa_payment['FirstName']
        originalCall.last_name = mpesa_payment['LastName']
        originalCall.amount = mpesa_payment['TransAmount']
        originalCall.txnRefNo = mpesa_payment['TransID']
        originalCall.updated_at = mpesa_payment['TransTime']
        originalCall.businessShortCode = mpesa_payment['BusinessShortCode']
        originalCall.transactionType = mpesa_payment['TransactionType']
        originalCall.transactionType = mpesa_payment['TransactionType']
        originalCall.save()

    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))


@csrf_exempt
def confirmation(request):
    mpesa_body = request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)
    mpesaPayment = mpesa_payment['Body']
    stkCallback = mpesaPayment['stkCallback']

    if stkCallback.__contains__('CallbackMetadata'):

        callbackMetadata = stkCallback['CallbackMetadata']
        merchantRequestId = stkCallback['MerchantRequestID']
        checkoutRequestId = stkCallback['CheckoutRequestID']
        items = callbackMetadata['Item']

        amount = None
        mpesaReceiptNumber = None
        transactionDate = None
        phoneNumber = None

        for item in items:
            name = item['Name']
            value = "Nil"
            if 'Value' in item:
                value = item['Value']

            if name == "Amount":
                amount = value
            elif name == "MpesaReceiptNumber":
                mpesaReceiptNumber = value
            elif name == "TransactionDate":
                transactionDate = value
            elif name == "PhoneNumber":
                phoneNumber = value

        stkRequest = StkPushCalls.objects.filter(checkoutRequestId=checkoutRequestId).order_by('-id')[0]
        stkRequest.amount = amount
        stkRequest.phoneNumber = phoneNumber
        stkRequest.merchantRequestId = merchantRequestId
        stkRequest.checkoutRequestId = checkoutRequestId
        stkRequest.customerMessage = "Payment received successfully"
        stkRequest.stkStatus = "Success"
        stkRequest.paymentStatus = "Success"
        stkRequest.statusReason = "Payment received successfully"
        stkRequest.txnRefNo = mpesaReceiptNumber
        stkRequest.transactionDate = transactionDate
        stkRequest.save()

        context = {
            "ResultCode": stkCallback['ResultCode'],
            "ResultDesc": stkCallback['ResultDesc']
        }

        print(dict(context))

        return JsonResponse(dict(context))
    else:
        context = {
            "ResultCode": stkCallback['ResultCode'],
            "ResultDesc": stkCallback['ResultDesc']
        }
        print(dict(context))
        return JsonResponse(dict(context))


@permission_classes((AllowAny,))
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

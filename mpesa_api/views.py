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
from mpesa_api.mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword

@csrf_exempt
@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
def getAccessToken(request):
    consumer_key = '6Gx2HNSCzyOMLLSCE1pCnDck6dGtR9bD'
    consumer_secret = 'GnPicfxhwfWWg0kY'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']
    return HttpResponse(validated_mpesa_access_token)


@csrf_exempt
@api_view(['GET', 'POST'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
def auto_check_payment(request):
    checkRequest = json.loads(request.body)

    try:
        data = StkPushCalls.objects.get(txnId=checkRequest['txnId'])
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

    except ObjectDoesNotExist:
        context = {
            "stkStatus": "Stk Not Received",
            "customerMessage": "Stk Not Received, Please Tap Again",
            "paymentStatus": "Failed",
            "statusReason": "Stk Not Received, Request the customer to Tap Again",
            "txnRefNo": "ACSVXCBDS",
            "customerName": "John Doe",
            "phoneNumber": "0700 0000000",
            "paidAmount": "0.00"
        }
        return JsonResponse(dict(context))


@csrf_exempt
@api_view(['GET', 'POST'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
def lipa_na_mpesa_online(request):
    stkRequest = json.loads(request.body)
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
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
        "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
        "AccountReference": stkRequest['merchantName'],
        "TransactionDesc": "PESAPAL SABI"
    }

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
            print("not saved ")

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
            paymentStatus=response.json()['errorMessage'],
            statusReason=response.json()['errorMessage'],
            txnId=stkRequest['txnId']
        )

        txnId = StkPushCalls.objects.all().filter(stkRequest['txnId']).exists()

        if not txnId.exists():
            stkRequestV1.save()

    return HttpResponse(response.text)


@csrf_exempt
@api_view(['GET', 'POST'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPpassword.Test_c2b_shortcode,
               "ResponseType": "Completed",
               "ConfirmationURL": "https://178.128.205.106/api/v1/c2b/confirmation",
               "ValidationURL": "https://178.128.205.106/api/v1/c2b/validation"}
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
@api_view(['GET', 'POST'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
def confirmation(request):
    global mpesaReceiptNumber, transactionDate

    mpesa_body = request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)
    mpesaPayment = mpesa_payment['Body']
    stkCallback = mpesaPayment['stkCallback']

    if stkCallback.__contains__('CallbackMetadata'):

        callbackMetadata = stkCallback['CallbackMetadata']
        merchantRequestId = stkCallback['MerchantRequestID']
        checkoutRequestId = stkCallback['CheckoutRequestID']
        items = callbackMetadata['Item']

        print(items)

        for item in items:
            print(item)
            name = item['Name']
            if name == 'MpesaReceiptNumber':
                mpesaReceiptNumber = item['Value']
                break
            if name == 'TransactionDate':
                transactionDate = item['Value']
                break

        print(mpesaReceiptNumber)
        print(transactionDate)

        context = {
            "ResultCode": stkCallback['ResultCode'],
            "ResultDesc": stkCallback['ResultDesc']
        }
        # print(dict(context))
        # push_service = FCMNotification(
        #     api_key="AAAA7k0KRjg:APA91bFOQD0g8Vd4AwtMNO841wBcyv7UnS_AyebMcj2kYIJhflfBKNqC_y3gKsUBEi08MMtCyxIMEvN_SR0ulkNtjD9PYDkMoTRGBaPed7UjNAHvr6PxGIxVyrl9Xs23BED5ZgpMpTMQ")
        # registration_id = "449376197dbb559"
        # message_title = "Success"
        # message_body = "Payment successful"
        # result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
        #                                            message_body=message_body)
        #
        # print(result)

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

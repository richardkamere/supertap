import json
from datetime import datetime

import requests
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from mpesa_api.serializers import UserSerializer

User = get_user_model()
from mpesa_api.models import StkPushCalls
from mpesa_api.mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword, MpesaC2bCredential, sendSuccessMessage, \
    sendFailedMessage, sendingSms


@csrf_exempt
def auto_check_payment(request):
    checkRequest = json.loads(request.body)
    data = StkPushCalls.objects.filter(txnId=checkRequest['txnId']).last()

    if data and data.paymentStatus == "Success":
        context = {
            "stkStatus": data.stkStatus,
            "customerMessage": data.customerMessage,
            "paymentStatus": data.paymentStatus,
            "statusReason": data.statusReason,
            "txnRefNo": data.txnRefNo,
            "customerName": data.first_name + ' ' + data.last_name + ' ' + data.middle_name,
            "phoneNumber": data.phoneNumber,
            "paidAmount": data.amount
        }

        return JsonResponse(dict(context))
    else:
        context = {
            "stkStatus": "Pending",
            "customerMessage": "Waiting for the customer to complete payment",
            "paymentStatus": "Failed",
            "statusReason": "Waiting for customer to initiate payment",
        }
        return JsonResponse(dict(context))


@csrf_exempt
def lipa_na_mpesa_online(request):
    stkRequest = json.loads(request.body)
    access_token = MpesaAccessToken().getAcessToken()
    api_url = MpesaC2bCredential.stk_push_url
    headers = {"Authorization": "Bearer %s" % access_token}
    print(stkRequest)
    request = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerBuyGoodsOnline",
        "Amount": stkRequest['amount'],
        "PartyA": stkRequest['phoneNumber'],  # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPpassword.Business_till_number,
        "PhoneNumber": stkRequest['phoneNumber'],  # replace with your phone number to get stk push
        "CallBackURL": MpesaC2bCredential.stk_push_callback_url,
        "AccountReference": stkRequest['merchantName'],
        "TransactionDesc": "CustomerPayBillOnline"
    }

    # check if the transaction exists
    if not StkPushCalls.objects.filter(txnId=stkRequest['txnId'], paymentStatus="Success").exists():
        response = requests.post(api_url, json=request, headers=headers)

        print(response.text)
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
                statusReason="Payment has not been received",
                txnId=stkRequest['txnId'],
                firebase_token=stkRequest['firebaseToken']
            )

            if not StkPushCalls.objects.filter(txnId=stkRequest['txnId']).exists():
                stkRequestV1.save()
            else:
                originalCall = StkPushCalls.objects.filter(txnId=stkRequest['txnId']).order_by('-id')[0]
                originalCall.checkoutRequestId = response.json()['CheckoutRequestID']
                originalCall.merchantRequestId = response.json()['CheckoutRequestID']
                originalCall.retryTimes = originalCall.retryTimes + 1
                originalCall.save()
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
                txnId=stkRequest['txnId'],
                firebase_token=stkRequest['firebaseToken']
            )
            sendFailedMessage(message=response.json()['errorMessage'],
                              device_id=stkRequestV1.firebase_token)
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
    access_token = MpesaAccessToken().getAcessToken()

    api_url = MpesaC2bCredential.register_url
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPpassword.Business_short_code,
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
    mpesa_payment = json.loads(request.body)

    print(mpesa_payment)
    print(mpesa_payment['MSISDN'])
    print(mpesa_payment['TransAmount'])
    print(mpesa_payment['BusinessShortCode'])

    if StkPushCalls.objects.filter(phoneNumber=mpesa_payment['MSISDN'], amount=mpesa_payment['TransAmount'],
                                   businessShortCode=mpesa_payment['BusinessShortCode']). \
            exclude(paymentStatus="Success").exists():
        print("details exists ...")
        originalCall = \
            StkPushCalls.objects.filter(phoneNumber=mpesa_payment['MSISDN'], amount=mpesa_payment['TransAmount'],
                                        businessShortCode=mpesa_payment['BusinessShortCode']).order_by('-id')[0]

        originalCall.first_name = mpesa_payment['FirstName']
        originalCall.last_name = mpesa_payment['LastName']
        originalCall.middle_name = mpesa_payment['MiddleName']
        originalCall.amount = mpesa_payment['TransAmount']
        originalCall.paymentStatus = "Success"
        originalCall.txnRefNo = mpesa_payment['TransID']
        originalCall.updated_at = mpesa_payment['TransTime']
        originalCall.businessShortCode = mpesa_payment['BusinessShortCode']
        originalCall.transactionType = mpesa_payment['TransactionType']
        originalCall.save()
        sendSuccessMessage(account=originalCall.accountReference, amount=originalCall.amount,
                           device_id=originalCall.firebase_token)

        username = mpesa_payment['FirstName'] + " " + mpesa_payment['LastName'] + " " + mpesa_payment['MiddleName']

        tnxDate = datetime.strptime(mpesa_payment['TransTime'], '%Y%m%d%H%M%S')

        sendSms = mpesa_payment['TransID'] + " Confirmed." + " Ksh" + mpesa_payment[
            'TransAmount'] + " received from " + username + " on " + str(tnxDate)

        sendingSms(message=sendSms)

    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }

    return JsonResponse(dict(context))


@csrf_exempt
def confirmation(request):
    mpesa_payment = json.loads(request.body)
    mpesaPayment = mpesa_payment['Body']
    stkCallback = mpesaPayment['stkCallback']
    merchantRequestId = stkCallback['MerchantRequestID']
    checkoutRequestId = stkCallback['CheckoutRequestID']
    stkRequest = StkPushCalls.objects.filter(checkoutRequestId=checkoutRequestId).order_by('-id')[0]
    stkRequest.merchantRequestId = merchantRequestId
    stkRequest.checkoutRequestId = checkoutRequestId
    firebaseToken = stkRequest.firebase_token

    if not stkCallback['ResultCode'] == 0:
        errorMessage = stkCallback['ResultDesc']
        stkRequest.customerMessage = errorMessage
        stkRequest.stkStatus = "Success"
        stkRequest.paymentStatus = "Failed"
        stkRequest.statusReason = errorMessage
        stkRequest.save()
        sendFailedMessage(message=stkRequest.customerMessage,
                          device_id=firebaseToken)

    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))


@permission_classes((AllowAny,))
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

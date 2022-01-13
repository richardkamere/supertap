import json

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
    sendFailedMessage


@csrf_exempt
def auto_check_payment(request):
    checkRequest = json.loads(request.body)
    data = StkPushCalls.objects.filter(txnId=checkRequest['txnId']).last()

    if data and (data.paymentStatus == "Success" or data.stkStatus == "Success"):
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
            "stkStatus": "Stk not received",
            "customerMessage": "Stk not received, Please tap again",
            "paymentStatus": "Failed",
            "statusReason": "Stk not received",
            "txnRefNo": "Nil",
            "customerName": "Nil",
            "phoneNumber": "Nil",
            "paidAmount": "0.00"
        }
        return JsonResponse(dict(context))


@csrf_exempt
def lipa_na_mpesa_online(request):
    stkRequest = json.loads(request.body)
    access_token = MpesaAccessToken().getAcessToken()
    headers = {"Authorization": "Bearer %s" % access_token}

    api_url = MpesaC2bCredential.stk_push_url
    request = {
        "merchant_reference": stkRequest['txnId'],
        "amount": stkRequest['amount'],
        "phone_number": stkRequest['phoneNumber'],
        "call_back_url": MpesaC2bCredential.confirmation_url,
        "description": stkRequest['merchantName'],
        "settlement_mapping_id": "c0e59031-5358-4aa0-815c-01b3c8d329e6",
        "customer_name": "",
        "reversal_notification_url": ""
    }

    # check if the transaction exists
    if not StkPushCalls.objects.filter(txnId=stkRequest['txnId'], paymentStatus="Success").exists():
        response = requests.post(api_url, json=request, headers=headers)

        jsonResponse = json.loads(response.text)
        print(stkRequest)

        if response.status_code == 200:
            stkRequestV1 = StkPushCalls(
                businessShortCode=jsonResponse['paybill_number'],
                request_code=jsonResponse['request_code'],
                transactionType='CustomerPayBillOnline',
                amount=stkRequest['amount'],
                partyA=stkRequest['phoneNumber'],
                partyB=jsonResponse['paybill_number'],
                phoneNumber=stkRequest['phoneNumber'],
                accountReference=stkRequest['merchantName'],
                transactionDesc=jsonResponse['message'],
                merchantRequestId=stkRequest['merchantName'],
                checkoutRequestId=stkRequest['merchantName'],
                responseCode=jsonResponse['status'],
                responseDescription=jsonResponse['message'],
                customerMessage=jsonResponse['message'],
                stkStatus="Success",
                paymentStatus="Pending",
                statusReason="Stk sent, Waiting for customer to complete payment",
                txnId=stkRequest['txnId'],
                firebase_token=stkRequest['firebaseToken']
            )

            if not StkPushCalls.objects.filter(txnId=stkRequest['txnId']).exists():
                stkRequestV1.save()
            else:
                originalCall = StkPushCalls.objects.filter(txnId=stkRequest['txnId']).order_by('-id')[0]
                originalCall.checkoutRequestId = stkRequest['merchantName']
                originalCall.merchantRequestId = stkRequest['merchantName']
                originalCall.request_code = jsonResponse['request_code']
                originalCall.retryTimes = originalCall.retryTimes + 1
                originalCall.save()
            context = {
                "ResponseCode": "0",
                "CustomerMessage": jsonResponse['message']
            }

            return JsonResponse(dict(context))
        else:
            stkRequestV1 = StkPushCalls(
                businessShortCode=jsonResponse['paybill_number'],
                transactionType='CustomerPayBillOnline',
                amount=stkRequest['amount'],
                partyA=stkRequest['phoneNumber'],
                partyB=jsonResponse['paybill_number'],
                phoneNumber=stkRequest['phoneNumber'],
                accountReference=stkRequest['merchantName'],
                transactionDesc=jsonResponse['message'],
                merchantRequestId=stkRequest['merchantName'],
                checkoutRequestId=stkRequest['merchantName'],
                responseCode=jsonResponse['status'],
                responseDescription=jsonResponse['message'],
                customerMessage=jsonResponse['message'],
                stkStatus="Failed",
                paymentStatus="Failed",
                statusReason=jsonResponse['message'],
                txnId=stkRequest['txnId'],
                request_code=jsonResponse['request_code'],
                firebase_token=stkRequest['firebaseToken']
            )
            sendFailedMessage(message=response.json()['errorMessage'],
                              device_id=stkRequestV1.firebase_token)
            if not StkPushCalls.objects.filter(txnId=stkRequest['txnId'], paymentStatus="Success").exists():
                stkRequestV1.save()

            context = {
                "ResponseCode": 1,
                "CustomerMessage": jsonResponse['message']
            }

            return JsonResponse(dict(context))

    else:
        context = {
            "ResponseCode": 1,
            "CustomerMessage": "Transaction has been complete, Please Tap your phone on the terminal again"
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
    originalCall = \
        StkPushCalls.objects.filter(request_code=mpesa_payment['request_code']).order_by('-id')[0]

    originalCall.first_name = "John"
    originalCall.last_name = "Due"
    originalCall.txnRefNo = mpesa_payment['confirmation_code']
    originalCall.updated_at = mpesa_payment['created_date']

    if mpesa_payment['payment_status_decription'] == "Completed":
        originalCall.paymentStatus = "Success"
        context = {
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        }
        sendSuccessMessage(account=originalCall.accountReference, amount=originalCall.amount,
                           device_id=originalCall.firebase_token)
    else:
        originalCall.paymentStatus = "Failed"
        context = {
            "ResultCode": 0,
            "ResultDesc": "Failed"
        }
        sendFailedMessage(message="Failed",
                          device_id=originalCall.firebase_token)

    originalCall.save()

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

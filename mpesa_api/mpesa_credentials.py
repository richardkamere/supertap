import requests
import json

from pyfcm import FCMNotification
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64


class MpesaC2bCredential:
    consumer_key = '588e69d9-3cf3-4cb8-a5d5-cbb43147b460'
    consumer_secret = '123dc986-8cb9-45db-a8f7-02f1080d295c'
    safaricom_base_url = 'https://mobile.pesapal.com/billsapi/'
    api_URL = safaricom_base_url + 'api/Authentication/RequestToken'
    base_url = 'https://7404-197-254-46-90.ngrok.io/'
    confirmation_url = base_url + 'api/v1/c2b/c2b_confirmation'
    validation_url = base_url + 'api/v1/c2b/validation'
    register_url = safaricom_base_url + 'mpesa/c2b/v1/registerurl'
    access_token_url = safaricom_base_url + 'oauth/v1/generate?grant_type=client_credentials'
    check_payment_status_url = safaricom_base_url + 'mpesa/c2b/v1/simulate'
    stk_push_url = safaricom_base_url + 'api/Transaction/PostMpesaRequest'
    stk_push_callback_url = base_url + 'api/v1/c2b/confirmation'


class MpesaAccessToken:

    def getAcessToken(self):
        request = {
            "consumer_key": MpesaC2bCredential.consumer_key,
            "consumer_secret": MpesaC2bCredential.consumer_secret
        }
        response = json.loads(requests.post(MpesaC2bCredential.api_URL, json=request).text)
        return response['token']


class LipanaMpesaPpassword:
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = "7528791"
    Business_till_number = "5541217"
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    data_to_encode = Business_short_code + passkey + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')
    customerBuyGoodsOnline = "CustomerBuyGoodsOnline"
    customerPayBillOnline = "CustomerPayBillOnline"


class FirebaseMessaging:
    api_key = "AAAAEiraDp0:APA91bEfi9ZZrAp0gCnF_Kb26uXIQ1V0Uz6jB2DooAjQUfSBjKMSOYWXpMpQ_PEEArMi6xsP_8hDS_-HUPH6shYnw3VGd-Hv-uZY0YdZtFf4HR3YLtkNl4K51Ba1czgZ_9RyxCpeY5fz"


def sendSuccessMessage(**kwargs):
    account = kwargs['account']
    amount = kwargs['amount']
    print(amount)
    print(account)
    push_service = FCMNotification(
        api_key=FirebaseMessaging.api_key)
    registration_id = kwargs['device_id']

    data_message = {
        "is_payment": True,
        "amount": amount,
        "payment_description": "Dear customer your payment for " + str(account) + " - " + str(amount) + ".00 has been processed"                                                                        "successfully",
        "title": "Transaction Successful",
        "status": "200",
        "is_mpesa": True
    }
    result = push_service.notify_single_device(registration_id=registration_id, data_message=data_message)
    print(result)


def sendFailedMessage(**kwargs):
    message = kwargs['message']
    push_service = FCMNotification(
        api_key=FirebaseMessaging.api_key)
    registration_id = kwargs['device_id']

    data_message = {
        "is_payment": True,
        "payment_description": "Dear customer your payment could not be completed",
        "title": "Mpesa Push Has Failed",
        "status": "500",
        "is_mpesa": True
    }
    result = push_service.notify_single_device(registration_id=registration_id, data_message=data_message)
    print(result)

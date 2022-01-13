import requests
import json

from pyfcm import FCMNotification
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64


class MpesaC2bCredential:
    consumer_key = 'kG3vJqUlANXmX9bSDA2SuLKYwA8v2lza'
    consumer_secret = 'Cx625lQX2NOmgVZv'
    safaricom_base_url = 'https://api.safaricom.co.ke/'
    api_URL = safaricom_base_url + 'oauth/v1/generate?grant_type=client_credentials'

    base_url = 'https://supertapdev.pesapalhosting.com/'
    confirmation_url = base_url + 'api/v1/c2b/c2b_confirmation'
    validation_url = base_url + 'api/v1/c2b/validation'
    register_url = safaricom_base_url + 'mpesa/c2b/v1/registerurl'
    access_token_url = safaricom_base_url + 'oauth/v1/generate?grant_type=client_credentials'
    check_payment_status_url = safaricom_base_url + 'mpesa/c2b/v1/simulate'
    stk_push_url = safaricom_base_url + 'mpesa/stkpush/v1/processrequest'
    stk_push_callback_url = base_url + 'api/v1/c2b/confirmation'

class MpesaAccessToken:

    def getAcessToken(self):
        r = requests.get(MpesaC2bCredential.api_URL,
                         auth=HTTPBasicAuth(MpesaC2bCredential.consumer_key, MpesaC2bCredential.consumer_secret))
        print(r)
        mpesa_access_token = json.loads(r.text)
        validated_mpesa_access_token = mpesa_access_token['access_token']
        return validated_mpesa_access_token


class LipanaMpesaPpassword:
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = "7528791"
    Business_till_number = "5541217"
    passkey = '5c702594ac2a13d87c51e419e39fe9430fe071c71f402d8d77aad52db7490137'
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
    push_service = FCMNotification(
        api_key=FirebaseMessaging.api_key)
    registration_id = kwargs['device_id']

    data_message = {
        "is_payment": True,
        "amount": amount,
        "payment_description": "Dear customer your payment for " + str(account) + "  " + str(amount) + " has been processed "
                                                                                            "successfully",
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
        "payment_description": "Dear customer your payment could not be completed due to " + message,
        "title": "Mpesa Push Has Failed",
        "status": "500",
        "is_mpesa": True
    }
    result = push_service.notify_single_device(registration_id=registration_id, data_message=data_message)
    print(result)

import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64


class MpesaC2bCredential:
    consumer_key = '6Gx2HNSCzyOMLLSCE1pCnDck6dGtR9bD'
    consumer_secret = 'GnPicfxhwfWWg0kY'
    safaricom_base_url = 'https://sandbox.safaricom.co.ke/'
    api_URL = safaricom_base_url + 'oauth/v1/generate?grant_type=client_credentials'

    # base_url = 'https://c9cb-197-232-34-48.ngrok.io/'
    base_url = 'https://d6bc-197-232-34-48.ngrok.io/'
    confirmation_url = base_url + 'api/v1/c2b/c2b_confirmation'
    validation_url = base_url + 'api/v1/c2b/validation'
    register_url = safaricom_base_url + 'mpesa/c2b/v1/registerurl'
    access_token_url = safaricom_base_url + 'oauth/v1/generate?grant_type=client_credentials'
    check_payment_status_url = safaricom_base_url + 'mpesa/c2b/v1/simulate'
    stk_push_url = safaricom_base_url + 'mpesa/stkpush/v1/processrequest'
    stk_push_callback_url = safaricom_base_url + 'api/v1/c2b/confirmation'


class MpesaAccessToken:
    r = requests.get(MpesaC2bCredential.api_URL,
                     auth=HTTPBasicAuth(MpesaC2bCredential.consumer_key, MpesaC2bCredential.consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']

    def getAcessToken(self):
        r = requests.get(MpesaC2bCredential.api_URL,
                         auth=HTTPBasicAuth(MpesaC2bCredential.consumer_key, MpesaC2bCredential.consumer_secret))
        mpesa_access_token = json.loads(r.text)
        validated_mpesa_access_token = mpesa_access_token['access_token']

        return validated_mpesa_access_token


class LipanaMpesaPpassword:
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = "174379"
    Test_c2b_shortcode = "600996"
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    data_to_encode = Business_short_code + passkey + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')
    customerBuyGoodsOnline = "CustomerBuyGoodsOnline"
    customerPayBillOnline = "CustomerPayBillOnline"

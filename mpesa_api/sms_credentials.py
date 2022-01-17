import requests
import json

from pyfcm import FCMNotification
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64


class SmsCredential:
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

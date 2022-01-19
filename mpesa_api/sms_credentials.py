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

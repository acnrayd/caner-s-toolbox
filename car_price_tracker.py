## Car price tracker
# This script tracks my car's price from an independent source, and writes to a CSV file with timestamp, on a daily basis

import requests
import json
import time
import csv
from datetime import datetime, timedelta

def get_auth_token():
    url = "https://app-vava-dtc-customer-tr-prod.azurewebsites.net/login"

    payload = "{\n  \"phone\": \"PHONE_NUMBER\",\n  \"password\": \"PASSWORD\"\n}"
    headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0',
      'Accept': 'application/json, text/plain, */*',
      'Accept-Language': 'en-US,en;q=0.5',
      'Content-Type': 'application/json',
      'Request-Id': '|52f1d6e38bfb45838f77450471d331f4.84167671af2643bb',
      'Request-Context': 'appId=cid-v1:cd1f4382-638e-4f3d-be0d-1ac2b69feacc',
      'traceparent': '00-52f1d6e38bfb45838f77450471d331f4-84167671af2643bb-01',
      'Content-Length': '56',
      'Origin': 'https://tr.vava.cars',
      'Connection': 'keep-alive',
      'Referer': 'https://tr.vava.cars/',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'cross-site',
      'Host': 'app-vava-dtc-customer-tr-prod.azurewebsites.net',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response = json.loads(response.text)
    global token
    token = response['accessToken']

def get_price():
    url = "https://app-vava-customer-portal-proxy-tr-prod.azurewebsites.net/v2/cust/api/Quotation/getDetails/PLAKA_ID"

    payload={}
    headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0',
      'Accept': 'application/json, text/plain, */*',
      'Accept-Language': 'tr-TR',
      'Authorization': 'Bearer ' + token,
      'x-application-key': 'CustomerPortal',
      'Request-Id': '|40a81e4831dd40b69672741eaf5cbbe2.2028578b275a4227',
      'Request-Context': 'appId=cid-v1:cd1f4382-638e-4f3d-be0d-1ac2b69feacc',
      'traceparent': '00-40a81e4831dd40b69672741eaf5cbbe2-2028578b275a4227-01',
      'Origin': 'https://tr.vava.cars',
      'Connection': 'keep-alive',
      'Referer': 'https://tr.vava.cars/',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'cross-site',
      'Content-Length': '0',
      'Host': 'app-vava-customer-portal-proxy-tr-prod.azurewebsites.net',
      'Cookie': 'TiPMix=5.933637335577602; x-ms-routing-name=self; ARRAffinity=722a7b7ecf7b68b9875341e7b1d7617057a0cb609da88f579eca40ed368ea8e4; ARRAffinitySameSite=722a7b7ecf7b68b9875341e7b1d7617057a0cb609da88f579eca40ed368ea8e4'
    }

    vava_response = requests.request("GET", url, headers=headers, data=payload)
    global fiyat
    fiyat = json.loads(vava_response.text)
    fiyat = fiyat["minPrice"]

def get_date():
    global tarih
    tarih = datetime.now()
    tarih = tarih.strftime("%d.%m.%Y")

def write_csv(filename, data):
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)
        file.close()

while True:
    get_auth_token()
    get_price()
    get_date()
    data = ["PLAKA_ID", tarih, fiyat]
    print(data)
    write_csv("vava.csv", data)

    time.sleep(86400)

## Sample test script to test Kaspersky Security Center API (KSC OpenAPI)

import requests
import base64
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ksc_server = "https://192.168.2.171:13299/"
url = ksc_server + "/api/v1.0/login"
user = "Automation"
password = "Automation"

user = base64.b64encode(user.encode('utf-8')).decode("utf-8")
password = base64.b64encode(password.encode('utf-8')).decode("utf-8")

session = requests.Session()

auth_headers = {
    'Authorization': 'KSCBasic user="' + user + '", pass="' + password + '", internal="1"',
    'Content-Type': 'application/json',
}

data = {}

response = session.post(url=url, headers=auth_headers, data=data, verify=False)
print(response)


url = ksc_server + "/api/v1.0/KlsrvoapiTestApi.TestMethod0"
common_headers = {
    'Content-Type': 'application/json',
}
data = {"caner": 3131}
response = session.post(url=url, headers=common_headers, data=json.dumps(data), verify=False)

responsejson = json.dump(response)

print(responsejson)

# This script is a basic PoC of Splunk + Phantom integration (without Splunk ES - Enterprise Security License)
# Without ES license, Splunk has no integration with Phantom (2019)
# In case of any port-scanning activity detected, firewall creates a simple log to Splunk. 
# I have created an alert in Splunk, in case of port-scanning activity log received on Splunk, it exports this record as CSV file and runs following script. 
# Basically this script does: 1) it creates a blank new container (event) in Phantom and gets generated "container_id" (which is unique event ID in Phantom. 
# We will use this ID to create artifacts under newly-generated event) 
# Then it gets Splunk log file from portscan.csv and fetches source_IP address of the attack. 
# Then it creates a new artifact under newly-created container and pushes src_ip from csv log under Phantom event as indicator. 
# Script is not suitable for your own usage out-of-the-box but will give you an idea about creating artifacts and events in Phantom.


import requests
import json
import csv
import random

####### Creating a container in Phantom - getting the container ID in response as "container_id" variable to script

url = "https://192.168.2.212/rest/container" ## DO NOT FORGET TO REPLACE YOUR PHANTOM IP

payload = "{\"parent_container\": null, \"node_guid\": null, \"in_case\": false, \"closing_rule_run\": null, \"sensitivity\": \"white\", \"closing_owner\": null, \"owner\": 1, \"ingest_app\": null, \"close_time\": null, \"open_time\": null, \"current_phase\": null, \"container_type\": \"default\", \"label\": \"events\",  \"version\": 1, \"role\": null, \"asset\": null, \"workflow_name\": \"\", \"status\": \"new\", \"owner_name\": null,  \"description\": \"\", \"tags\": [\"port_scan\"], \"kill_chain\": null, \"data\": {}, \"custom_fields\": {}, \"severity\": \"low\", \"tenant\": 0, \"name\": \"Port_Scanner\", \"end_time\": null, \"container_update_time\": null}"
headers = {
    'ph-auth-token': "PFf1qGLZpw5gr4hhBv0ze0GzjPcAGZmveZc32ss4dek=", ### PHANTOM AUTHORIZATION TOKEN
    'content-type': "application/json",
    'cache-control': "no-cache",
    'postman-token': "253980f6-a72a-5f06-7bc1-04c13a02c150"
    }

response = requests.request("POST", url, data=payload, headers=headers, verify=False)

global x
x= json.loads(response.text)

container_id = (x["id"])
status =(x["success"])
print(x)

if status == True:
    print(x)
else:
    exit()

##### Importing CSV data and getting IP address (src_ip value)

splunk_alert_csv = open("/opt/splunk/etc/apps/search/lookups/portscan.csv", "r") ## SPLUNK EXPORTED LOOKUP TABLE PATH

reader = csv.DictReader(splunk_alert_csv, delimiter=",")
for row in reader:
    global src_ip
    src_ip= (row["src_ip"])


##### Importing Artifact as Python Dictionary, replacing container_id with real value, replacing src_ip with real value

artifact_json_original = '{ "container_id": 35, "severity": "low", "cef": {"sourceAddress": "192.168.2.5"}, "name": "Source_IP", "description": "Caner"}'

artifact_json_imported: object = json.loads(artifact_json_original)

#src_ip_imported = artifact_json_imported['cef']['sourceAddress']

artifact_json_imported['cef']['sourceAddress']= src_ip

print(artifact_json_imported['cef']['sourceAddress'])

artifact_json_imported["container_id"] = container_id

rastgele=random.randint(1,9999)

artifact_json_imported["description"] = rastgele

artifact_json_exported = json.dumps(artifact_json_imported)

print(artifact_json_exported)

### Pushing artifact to Phantom

url2 = "https://192.168.2.212/rest/artifact/" ### DO NOT FORGET TO REPLACE YOUR PHANTOM IP
payload = (artifact_json_exported)

headers = {
    'ph-auth-token': "PFf1qGLZpw5gr4hhBv0ze0GzjPcAGZmveZc32ss4dek=", ### PHANTOM AUTHORISATION TOKEN
    'content-type': "application/json",
    'cache-control': "no-cache",
    }

response = requests.request("POST", url2, data=payload, headers=headers, verify=False)

print(response.text)

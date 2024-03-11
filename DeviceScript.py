import subprocess
import json
import getpass
from datetime import datetime

# Parameters
username = "placeholder"
password = getpass.getpass(prompt="Password: ", stream=None) 

url = "https://placeholder.jamfcloud.com"
csvFileName = "Devices.csv"

# see all on possible parameters on https://developer.jamf.com/jamf-pro/reference/patch_v2-mobile-devices-id
bodyJson="""{
    "ios": {
        "purchasing": {
            "leased": true,
            "purchased": false,
            "poDate": "2023-05-01T00:00:00.000Z",
            "leaseExpiresDate": "2026-04-30T00:00:00.000Z",
    	    "vendor": "Placeholder"
        }
    }
}"""

# token
bearerToken = ""

# login
def getBearerToken():
    global bearerToken
    response = subprocess.check_output(['curl', '-s', '-u', f'{username}:{password}', f'{url}/api/v1/auth/token', '-X', 'POST']).decode('utf-8')
    response_json = json.loads(response)
    bearerToken = response_json.get('token')

def serialNrToId(serialNr):
    # do a search with a serialNumber filter. that way the response will only contain the info of one computer
    requestUrl = f"{url}/api/v2/mobile-devices/detail?section=GENERAL&page=0&page-size=100&sort=displayName%3Aasc&filter=serialNumber%3D%3D%22{serialNr}%22"
    result = subprocess.check_output(['curl', '-s', '-X', 'GET', requestUrl, '-H', 'accept: application/json', '-H', f'Authorization: Bearer {bearerToken}']).decode('utf-8')
    resultJson = json.loads(result)
    deviceList = resultJson.get('results')
    if (len(deviceList) == 0):
        return -1
    deviceInfo = deviceList[0]
    return deviceInfo.get('mobileDeviceId')

def updatePurchasing(id):
    subprocess.check_output(['curl', '--request', 'PATCH', '--url', f'{url}/api/v2/mobile-devices/{id}', '-H', 'Content-Type: application/json', '-H', 'accept: application/json', '-H', f'Authorization: Bearer {bearerToken}', '-d', bodyJson])


getBearerToken()
with open(csvFileName, 'r') as file:
    for line in file:
        serialNr = line.strip()
        id = serialNrToId(serialNr)
        if (id != -1):
            updatePurchasing(id)

print("done");

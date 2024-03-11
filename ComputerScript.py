import subprocess
import json
import getpass
from datetime import datetime

# Parameters
username = "placeholder"
password = getpass.getpass(prompt="Password: ", stream=None) 

url = "https://placeholder.jamfcloud.com"
csvFileName = "Laptops.csv"

# see all on possible parameters on https://developer.jamf.com/jamf-pro/reference/patch_v1-computers-inventory-detail-id
bodyJson="""
	{
		"purchasing": {
    			"leased": false,
    			"purchased": true,
    			"poDate": "2023-03-15",
    			"vendor": "Placeholder"
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
    requestUrl = f"{url}/api/v1/computers-inventory?section=GENERAL&page=0&page-size=100&sort=general.name%3Aasc&filter=hardware.serialNumber%3D%3D%22{serialNr}%22"
    result = subprocess.check_output(['curl', '-s', '-X', 'GET', requestUrl, '-H', 'accept: application/json', '-H', f'Authorization: Bearer {bearerToken}']).decode('utf-8')
    resultJson = json.loads(result)
    computerList = resultJson.get('results')
    if (len(computerList) == 0):
        return -1
    computerInfo = computerList[0]
    return computerInfo.get('id')

def updatePurchasing(id):
    subprocess.check_output(['curl', '--request', 'PATCH', '--url', f'{url}/api/v1/computers-inventory-detail/{id}', '-H', 'Content-Type: application/json', '-H', 'accept: application/json', '-H', f'Authorization: Bearer {bearerToken}', '-d', bodyJson])


getBearerToken()
with open(csvFileName, 'r') as file:
    for line in file:
        serialNr = line.strip()
        id = serialNrToId(serialNr)
        if (id != 0):
            updatePurchasing(id)

print("done")

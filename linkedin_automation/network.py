import requests
import random
import time
import json

COOKIES_FILE = 'cookies.json'
HEADERS_FILE = 'headers.json'

def load_data_from_file(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    return data


def build_and_send_request(id,msg):
    cookies = load_data_from_file(COOKIES_FILE)
    headers = load_data_from_file(HEADERS_FILE)

    params = {
        'action': 'verifyQuotaAndCreate',
        'decorationId': 'com.linkedin.voyager.dash.deco.relationships.InvitationCreationResultWithInvitee-2',
    }
    json_data = {}
    if msg:
        json_data = {
            'inviteeProfileUrn': 'urn:li:fsd_profile:' + id,
            'customMessage': msg,
        }
    else:
        json_data = {
            'inviteeProfileUrn': 'urn:li:fsd_profile:' + id,
        }
    response = requests.post(
        'https://www.linkedin.com/voyager/api/voyagerRelationshipsDashMemberRelationships',
        params=params,
        cookies=cookies,
        headers=headers,
        json=json_data,
    )

    wait_time = random.randint(15, 45)  # Generate a random integer between 15 and 45
    print(f"\r\nWaiting {wait_time} seconds")
    time.sleep(wait_time)
    return response.status_code
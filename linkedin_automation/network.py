import requests
import random
import time
import json
import datetime

COOKIES_FILE = 'cookies.json'
HEADERS_FILE = 'headers.json'
OUR_PUBLIC_IDS = ['lior-saddan-b88a1013a', 'or-ron-5aa1aa15', 'itzikmizrachi']


def load_data_from_file(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    return data


def build_and_send_request(id, msg):
    cookies = load_data_from_file(COOKIES_FILE)
    headers = load_data_from_file(HEADERS_FILE)

    params = {
        'action': 'verifyQuotaAndCreate',
        'decorationId': 'com.linkedin.voyager.dash.deco.relationships.InvitationCreationResultWithInvitee-2',
    }

    json_data = {
        'inviteeProfileUrn': 'urn:li:fsd_profile:' + id,
        'customMessage': msg,
    }
    response = requests.post(
        'https://www.linkedin.com/voyager/api/voyagerRelationshipsDashMemberRelationships',
        params=params,
        cookies=cookies,
        headers=headers,
        json=json_data,
    )

    # Generate a random integer between 15 and 45
    wait_time = random.randint(15, 45)
    print(f"\r\nWaiting {wait_time} seconds")
    time.sleep(wait_time)
    return response.status_code


def get_connection_state(profile):
    cookies = load_data_from_file(COOKIES_FILE)
    headers = load_data_from_file(HEADERS_FILE)

    params = {
        'decorationId': 'com.linkedin.voyager.dash.deco.identity.profile.TopCardSupplementary-130',
        'q': 'memberIdentity',
        'memberIdentity': profile,
    }

    response = requests.get(
        'https://www.linkedin.com/voyager/api/identity/dash/profiles',
        params=params,
        cookies=cookies,
        headers=headers,
    )

    is_connected = None
    invitation_state = None
    invitation_type = None
    public_identifier = None
    # Parse response to locate memberRelationshipUnion
    response_json = response.json()
    included = response_json['included']
    for attribute in included:
        if 'memberRelationshipUnion' in attribute:
            memberRelationshipUnion = attribute['memberRelationshipUnion']
            if 'noConnection' in memberRelationshipUnion:
                is_connected = False
            elif '*connection' in memberRelationshipUnion:
                is_connected = True
        if 'invitationState' in attribute and attribute['invitationState'] is not None:
            invitation_state = attribute['invitationState'].lower()

        if 'invitationType' in attribute and attribute['invitationType'] is not None:
            invitation_type = attribute['invitationType'].lower()
        if 'memberRelationshipData' in attribute:
            if 'noInvitation' in attribute['memberRelationshipData']:
                invitation_state = 'not_sent'
        if 'publicIdentifier' in attribute and attribute['publicIdentifier'] not in OUR_PUBLIC_IDS:
            public_identifier = attribute['publicIdentifier']

    res = {'is_connected': is_connected,
           'invitation_state': invitation_state,
           'invitation_type': invitation_type,
           'public_identifier': public_identifier,
           'ts': str(datetime.datetime.now())}

    wait_time = random.randint(1, 4)
    print(f"\r\nWaiting {wait_time} seconds")
    time.sleep(wait_time)
    return res

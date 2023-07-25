import requests
import random
import time
import json
import datetime
import os

OUR_PUBLIC_IDS = ['lior-saddan-b88a1013a', 'or-ron-5aa1aa15', 'itzikmizrachi']


def load_data_from_file(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    return data


class NetworkSender():
    def __init__(self, path_to_cookies, path_to_headers):
        if path_to_cookies.endswith('.json'):
            self.cookies = load_data_from_file(path_to_cookies)
        else:
            self.cookies = json.loads(os.environ['LINKEDIN_COOKIES'])

        if path_to_headers.endswith('.json'):
            self.headers = load_data_from_file(path_to_headers)
        else:
            self.headers = json.loads(os.environ['LINKEDIN_HEADERS'])
        print(f"Headers:{self.headers}\r\n\r\nCookies{self.cookies}")

    def build_and_send_request(self, linkedin_id, msg):
        params = {
            'action': 'verifyQuotaAndCreate',
            'decorationId': 'com.linkedin.voyager.dash.deco.relationships.InvitationCreationResultWithInvitee-2',
        }
        json_data = {}
        if msg:
            json_data = {
                'inviteeProfileUrn': 'urn:li:fsd_profile:' + linkedin_id,
                'customMessage': msg,
            }
        else:
            json_data = {
                'inviteeProfileUrn': 'urn:li:fsd_profile:' + linkedin_id,
            }
        response = requests.post(
            'https://www.linkedin.com/voyager/api/voyagerRelationshipsDashMemberRelationships',
            params=params,
            cookies=self.cookies,
            headers=self.headers,
            json=json_data,
        )

        return response

    def get_connection_state(self, profile):
        params = {
            'decorationId': 'com.linkedin.voyager.dash.deco.identity.profile.TopCardSupplementary-130',
            'q': 'memberIdentity',
            'memberIdentity': profile,
        }

        response = requests.get(
            'https://www.linkedin.com/voyager/api/identity/dash/profiles',
            params=params,
            cookies=self.cookies,
            headers=self.headers,
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
        return res

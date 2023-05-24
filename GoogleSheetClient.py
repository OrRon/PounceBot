
import gspread
import time
import json
from google.oauth2.service_account import Credentials
SCOPES = ['https://www.googleapis.com/auth/drive',
 'https://www.googleapis.com/auth/drive.file',
 'https://www.googleapis.com/auth/spreadsheets']
# Load the credentials from the JSON key file



class GoogleSheetClient:
    def __init__(self, path_to_credentials, sheet_name, inner_sheet_name, owner_name):
        credentials = Credentials.from_service_account_file(path_to_credentials, scopes=SCOPES)
        self.client = gspread.authorize(credentials)
        self.sheet = self.client.open(sheet_name).worksheet(inner_sheet_name)
        self.owner_name = owner_name


    def add_or_update_missing_entries(self, entry):
        print(entry)
        key = entry['profile']
        cell = self.sheet.find(key)
        if not cell: # if the key is not found
            profile = entry['profile']
            full_name = ''
            reachout_name = entry['reachout_name']
            activity_log = json.dumps([{
                            'result':entry['result'],
                            'type':'linked_in_connect_request',
                            'reachout_by': self.owner_name,
                            'ts':'',
                            'message':entry['message']}])
            reached_out_by = self.owner_name
            self.sheet.append_row([profile,
                                    full_name,
                                    reachout_name,
                                    activity_log,
                                    reached_out_by])

def main():
    pass



if __name__ == '__main__':
    main()
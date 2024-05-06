
import gspread
import datetime
import json
import os
import argparse
from google.oauth2.service_account import Credentials
SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/spreadsheets']
# Load the credentials from the JSON key file


class GoogleSheetClient:
    def __init__(self, path_to_credentials, sheet_name, inner_sheet_name, owner_name):
        credentials = None
        if path_to_credentials == 'env':
            creds = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT'])
            credentials = Credentials.from_service_account_info(
                creds, scopes=SCOPES)
        else:
            credentials = Credentials.from_service_account_file(
                path_to_credentials, scopes=SCOPES)
        self.client = gspread.authorize(credentials)
        self.sheet = self.client.open(sheet_name).worksheet(inner_sheet_name)
        self.owner_name = owner_name
        self.buffered_entries = []
        self.buffer_size = 50

    def flush(self):
        print(f"Flush, len {len(self.buffered_entries)}")
        self.sheet.append_rows(self.buffered_entries)
        self.buffered_entries = []
        print(f"After Flush, len {len(self.buffered_entries)}")

    def delete_row(self, key):
        cell = self.sheet.find(key)
        if cell:
            self.sheet.delete_row(cell.row)
            return True
        return False

    def get_row(self, key):
        cell = self.sheet.find(key)
        if cell:
            return self.sheet.row_values(cell.row)
        return None

    def has_been_reached_out_by_current_user(self, key):
        row = self.get_row(key)
        if row == None:
            return False
        reached_out_by = json.loads(row[4])
        return self.owner_name in reached_out_by

    def reached_out_by_current_user(self, entry):
        key = entry['linkedin_profile_link']
        cell = self.sheet.find(key)
        if not cell:  # if the key is not found
            return False

        row = self.sheet.row_values(cell.row)
        return self.owner_name in json.loads(row[4])

    def update_row_state(self, entry, state):
        key = entry['linkedin_profile_link']
        cell = self.sheet.find(key)
        if not cell:  # if the key is not found
            raise Exception('entry doesnt exist' + str(entry))

        row = self.sheet.row_values(cell.row)

        has_reached_out = state['is_connected'] or state['invitation_type'] == 'sent'
        if has_reached_out:
            reached_out_by = json.loads(row[4])
            merged_reached_out_by = json.dumps(
                list(set(reached_out_by + [self.owner_name])))
            row[4] = merged_reached_out_by
        elif state['invitation_state'] == 'not_sent':  # remove if not reached out
            reached_out_by = json.loads(row[4])
            if self.owner_name in reached_out_by:
                reached_out_by.remove(self.owner_name)
                row[4] = json.dumps(reached_out_by)

        reachout_state = {}
        try:
            reachout_state = json.loads(row[8])
        except:
            pass

        if 'public_identifier' in state:
            row[9] = state.pop('public_identifier')

        reachout_state[self.owner_name.lower()] = state
        row[8] = json.dumps(reachout_state)
        self.sheet.update(f"A{cell.row}:ZZ{cell.row}", [row])

    def add_or_update_missing_entries(self, entry, flush=True):
        if (entry['result'] != 'success' and entry['result'] != 'blocked' and entry['result'] != 'pending'):
            return
        key = entry['linkedin_profile_link']
        cell = self.sheet.find(key)
        if not cell:  # if the key is not found
            role = json.dumps(
                ['unknown']) if 'role' not in entry else entry['role']
            email = ''
            had_meeting = '0'
            profile = entry['linkedin_profile_link']
            full_name = ''
            reachout_name = entry['reachout_name']
            activity_log = json.dumps([{
                'result': entry['result'],
                'type':'linked_in_connect_request',
                'reachout_by': self.owner_name,
                'ts':str(datetime.datetime.now()),
                'message':entry['message']}])
            reached_out_by = json.dumps([self.owner_name])
            state = '{}'
            public_identifier = ''
            junk = '0' # Add this so that we could get a row with a null public_id
            row = [profile,
                   full_name,
                   reachout_name,
                   activity_log,
                   reached_out_by,
                   had_meeting,
                   role,
                   email,
                   state,
                   public_identifier,
                   junk]
            self.buffered_entries.append(row)
            if flush or len(self.buffered_entries) >= self.buffer_size:
                self.flush()
        else:  # if the key is found
            row = self.sheet.row_values(cell.row)
            merged_activity_log = json.dumps(json.loads(row[3]) + [{
                'result': entry['result'],
                'type':'linked_in_connect_request',
                'reachout_by': self.owner_name,
                'ts':str(datetime.datetime.now()),
                'message':entry['message']}])
            row[3] = merged_activity_log
            reached_out_by = json.loads(row[4])
            merged_reached_out_by = json.dumps(
                list(set(reached_out_by + [self.owner_name])))
            row[4] = merged_reached_out_by
            if 'role' in entry:
                row[6] = entry['role']
            self.sheet.update(f"A{cell.row}:ZZ{cell.row}", [row])



def get_keys_from_sheet(s):
    entries = s.sheet.get_all_records()
    return set([r['linkedin_profile_link'] for r in entries])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", help="name_of_sheet")
    args = parser.parse_args()

    db_sheet_client = GoogleSheetClient('env', 'reachout_script_db', 'main', '')
    src_sheet_client = GoogleSheetClient('env', 'reachout_script_db', args.src, '')
    diff = get_keys_from_sheet(src_sheet_client) - get_keys_from_sheet(db_sheet_client)
    print(diff)



if __name__ == '__main__':
    main()

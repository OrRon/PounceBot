
import gspread
import datetime
import csv
import json
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
# Load the credentials from the JSON key file


class GoogleCalendarClient:
    def __init__(self, path_to_credentials, calendar_id, days_back, output_file):
        credentials = Credentials.from_service_account_file(
            path_to_credentials, scopes=SCOPES)
        self.client = build('calendar', 'v3', credentials=credentials)
        self.calendar_id = calendar_id
        # Calculate the start and end dates for the query
        self.end_date = (datetime.utcnow() + timedelta(days=60)).isoformat()  + 'Z'
        self.start_date = (datetime.utcnow() -
                           timedelta(days=days_back)).isoformat() + 'Z'
        self.blocklisted_event_names = ['starting time', 'date night',
                                        'התור שהזמנת למרפאה בכללית', 'weekly planning', 'px sync', 'px catchup', 'guy@lewin.co.il   ']
        self.unrelated_emails = set(
            ['saddanunicorn@gmail.com', 'hadarro12@gmail.com', 'asafmdr@gmail.com', 'pborisp@gmail.com', 'iliagore@gmail.com'])
        self.output_file = output_file

    def include_event(self, e):
        if 'summary' in e:
            summary = e['summary'].lower()
            if summary in self.blocklisted_event_names:
                return False

        attendees = e.get('attendees', [])
        if len(attendees) < 2:
            return False

        emails = set([a['email'] for a in attendees])

        if len(emails.intersection(self.unrelated_emails)) > 0:
            return False

        return True

    def print_events(self):
        # Display the events with title and participants
        # Call the API to fetch events
        events_result = self.client.events().list(calendarId=self.calendar_id,
                                                  timeMin=self.start_date, timeMax=self.end_date).execute()
        unfiltered_events = events_result.get('items', [])

        # Filter events by name
        events = [
            event for event in unfiltered_events if self.include_event(event)
        ]

        if not events:
            print('No events found.')
        else:
            print('Events:')
            for event in events:
                start = event['start'].get(
                    'dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No title')
                attendees = event.get('attendees', [])

                print(f'{start} - {summary}')
                if attendees:
                    print('Attendees:')
                    for attendee in attendees:
                        print(attendee['email'])
                print()
        
                # Write events to CSV file
        with open(self.output_file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Start', 'Summary', 'Attendees'])

            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No title')
                attendees = event.get('attendees', [])
                emails = set([a['email'] for a in attendees])
                writer.writerow([start, summary, emails])

        print(f'Filtered events saved to {self.output_file} as CSV.')


def main():
    path_to_credentials = '/home/lsaddan/keys/google_service_account.json'
    # Call the API to fetch events
    calendar_id = 'lior.saddan.93@gmail.com'
    # calendar_id = '11f363fb6d4603698a5f8ff887c465430fb4103a955b69ba5d924ba284bbe7bc@group.calendar.google.com'

    days_back = 65
    client = GoogleCalendarClient(
        path_to_credentials, calendar_id, days_back, 'meetings.csv')
    client.print_events()


if __name__ == '__main__':
    main()

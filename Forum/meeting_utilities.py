from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import datetime
import pytz

# Set up the credentials object
creds = Credentials.from_authorized_user_file('credentials/credentials.json', ['https://www.googleapis.com/auth/calendar'])


def generate_link():
    # Set up the Calendar API client
    service = build('calendar', 'v3', credentials=creds)

    # Set up the event details
    event = {
        'summary': 'Example Event',
        'location': '123 Main St, Anytown USA',
        'description': 'This is an example event.',
        'start': {
            'dateTime': '2023-07-28T09:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': '2023-07-28T17:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'conferenceData': {
            'createRequest': {
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet'
                },
                'requestId': '<random-string>'
            }
        },
    }

    # Create the event
    event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()

    # Print out the event ID and conference link
    print(f'Event created: {event.get("htmlLink")}')
    print(f'Conference link: {event.get("conferenceData").get("entryPoints")[0].get("uri")}')

    return True

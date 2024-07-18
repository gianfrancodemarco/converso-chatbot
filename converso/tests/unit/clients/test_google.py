from datetime import datetime
from unittest.mock import MagicMock, patch

from google.oauth2.credentials import Credentials

from converso.clients.google import (CreateCalendarEventPayload,
                                     GetCalendarEventsPayload,
                                     GetEmailsPayload, GoogleClient)


def test_create_calendar_event():
    credentials = MagicMock(spec=Credentials)
    client = GoogleClient(credentials)

    payload = CreateCalendarEventPayload(
        summary="Test Event",
        description="This is a test event",
        start=datetime(2022, 1, 1, 10, 0),
        end=datetime(2022, 1, 1, 12, 0),
    )

    # Mock the build and events().insert().execute() methods
    service_mock = MagicMock()
    events_mock = MagicMock()
    events_mock.insert.return_value.execute.return_value = {"id": "12345"}
    service_mock.events.return_value = events_mock

    with patch('converso.clients.google.build', return_value=service_mock):
        client.create_calendar_event(payload)

    # Verify that the event was created
    events_mock.insert.assert_called_once_with(
        calendarId='primary',
        body={
            'summary': 'Test Event',
            'description': 'This is a test event',
            'start': {'dateTime': '2022-01-01T10:00:00', 'timeZone': 'UTC'},
            'end': {'dateTime': '2022-01-01T12:00:00', 'timeZone': 'UTC'},
        }
    )
    events_mock.insert.return_value.execute.assert_called_once()


def test_get_calendar_events():
    credentials = MagicMock(spec=Credentials)
    client = GoogleClient(credentials)

    payload = GetCalendarEventsPayload(
        start=datetime(2022, 1, 1, 0, 0),
        end=datetime(2022, 1, 7, 0, 0),
    )

    # Mock the build and events().list().execute() methods
    service_mock = MagicMock()
    events_mock = MagicMock()
    events_mock.list.return_value.execute.return_value = {
        'items': [
            {'summary': 'Event 1'},
            {'summary': 'Event 2'},
            {'summary': 'Event 3'},
        ]
    }
    service_mock.events.return_value = events_mock

    with patch('converso.clients.google.build', return_value=service_mock):
        events = client.get_calendar_events(payload)

    # Verify that the correct events were retrieved
    events_mock.list.assert_called_once_with(
        calendarId='primary',
        timeMin='2022-01-01T00:00:00+00:00',
        timeMax='2022-01-07T00:00:00+00:00',
        singleEvents=True,
        orderBy='startTime',
    )
    events_mock.list.return_value.execute.assert_called_once()
    assert len(events) == 3
    assert events[0]['summary'] == 'Event 1'
    assert events[1]['summary'] == 'Event 2'
    assert events[2]['summary'] == 'Event 3'


def test_get_calendar_events_html():
    credentials = MagicMock(spec=Credentials)
    client = GoogleClient(credentials)

    payload = GetCalendarEventsPayload(
        start=datetime(2022, 1, 1, 0, 0),
        end=datetime(2022, 1, 7, 0, 0),
    )

    # Mock the build and events().list().execute() methods
    service_mock = MagicMock()
    events_mock = MagicMock()
    events_mock.list.return_value.execute.return_value = {
        'items': [
            {
                'summary': 'Event 1',
                'htmlLink': 'www.test.com',
                'start': {
                    'dateTime': '2022-01-01T00:00:00+00:00'
                },
                'end': {
                    'dateTime': '2022-02-01T00:00:00+00:00'
                }
            },
            {
                'summary': 'Event 2',
                'htmlLink': 'www.test.com',
                'start': {
                    'dateTime': '2022-01-01T00:00:00+00:00'
                },
                'end': {
                    'dateTime': '2022-02-01T00:00:01+00:00'
                }
            }
        ]
    }
    service_mock.events.return_value = events_mock

    with patch('converso.clients.google.build', return_value=service_mock):
        events = client.get_calendar_events_html(payload)

    # Verify that the correct events were retrieved
    events_mock.list.assert_called_once_with(
        calendarId='primary',
        timeMin='2022-01-01T00:00:00+00:00',
        timeMax='2022-01-07T00:00:00+00:00',
        singleEvents=True,
        orderBy='startTime',
    )
    events_mock.list.return_value.execute.assert_called_once()
    assert events == '1. 2022-01-01T00:00:00+00:00 - <a href="www.test.com">Event 1</a>\n2. 2022-01-01T00:00:00+00:00 - <a href="www.test.com">Event 2</a>\n'


def test_get_emails():
    credentials = MagicMock(spec=Credentials)
    client = GoogleClient(credentials)

    payload = GetEmailsPayload(number_of_emails=3)

    service_mock = MagicMock()
    service_mock.users.return_value.messages.return_value.list.return_value.execute.return_value = {
        'messages': [
            {'id': '12345'},
            {'id': '67890'},
        ]
    }
    service_mock.users.return_value.messages.return_value.get.return_value.execute.return_value = {
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'Date', 'value': '2022-01-01'},
                {'name': 'Subject', 'value': 'Test Email'},
            ]
        },
        'snippet': 'This is a test email'
    }

    with patch('converso.clients.google.build', return_value=service_mock):
        emails = client.get_emails(payload)

    service_mock.users.assert_called()
    service_mock.users.return_value.messages.assert_called()
    service_mock.users.return_value.messages.return_value.list.assert_called_with(
        userId='me',
        maxResults=3,
    )

    assert len(emails) == 2
    assert emails[0]['sender'] == 'sender@example.com'
    assert emails[0]['time'] == '2022-01-01'
    assert emails[0]['subject'] == 'Test Email'
    assert emails[0]['content'] == 'This is a test email'


def test_get_emails():
    credentials = MagicMock(spec=Credentials)
    client = GoogleClient(credentials)

    payload = GetEmailsPayload(number_of_emails=3)

    service_mock = MagicMock()
    service_mock.users.return_value.messages.return_value.list.return_value.execute.return_value = {
        'messages': [
            {'id': '12345'},
            {'id': '67890'},
        ]
    }
    service_mock.users.return_value.messages.return_value.get.return_value.execute.return_value = {
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'Date', 'value': '2022-01-01'},
                {'name': 'Subject', 'value': 'Test Email'},
            ],
            'mimeType': 'text/plain',
            'body': {
                'data': 'VGhpcyBpcyBhIHRlc3QgZW1haWw='
            }
        },
        'snippet': 'This is a test email'
    }

    with patch('converso.clients.google.build', return_value=service_mock):
        emails = client.get_emails_html(payload)

    service_mock.users.assert_called()
    service_mock.users.return_value.messages.assert_called()
    service_mock.users.return_value.messages.return_value.list.assert_called_with(
        userId='me',
        maxResults=3,
    )

    assert emails == "\n1. Subject: Test Email\nSender: sender@example.com\nTime: 2022-01-01\nContent: This is a test email\n\n\n\n\n2. Subject: Test Email\nSender: sender@example.com\nTime: 2022-01-01\nContent: This is a test email\n\n\n\n"

import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
import time

import config


class GoogleApiClient:

    def __init__(self):
        self.CREDENTIALS_FILE = config.filepath
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(self.CREDENTIALS_FILE, [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'])
        self.httpAuth = self.credentials.authorize(httplib2.Http())

        # creating drive service object for API v4
        self.service_v4 = apiclient.discovery.build('sheets', 'v4', http=self.httpAuth)
        # creating drive service object for API v3
        self.service_v3 = apiclient.discovery.build('drive', 'v3', http=self.httpAuth)


class File (GoogleApiClient):

    def __init__(self):
        super().__init__()

        self.spreadsheet = None
        self.spreadsheetId = None
        self.spreadsheetUrl = None
        self.title = None

    def create_file(self, title=None):
        self.title = title if title else 'Сие есть название документа'
        self.spreadsheet = self.service_v4.spreadsheets().create(body={
            'properties': {'title': self.title, 'locale': 'ru_RU'},
            'sheets': [{'properties': {'sheetType': 'GRID',
                                       'sheetId': 0,
                                       'title': 'Сие есть название листа',
                                       'gridProperties': {'rowCount': 8, 'columnCount': 5}}}]
        }).execute()

        # id of the created file
        self.spreadsheetId = self.spreadsheet['spreadsheetId']

        # url of the created file
        self.spreadsheetUrl = self.spreadsheet['spreadsheetUrl']

        # changes owner of the created file from service account to real user by email
        time.sleep(5)
        File.change_owner(self)

        # prints url of the created file
        print('\nOpen me: %s\n' % self.spreadsheetUrl)

    def update_file(self):
        pass

    def del_file(self):
        pass

    def find_files(self):
        page_token = None
        while True:
            response = self.service_v3.files().list(q="name = 'Сие есть название документа'",
                                                      spaces='drive',
                                                      fields='nextPageToken, files(id, name, owners)',
                                                      pageToken=page_token).execute()
            for file in response.get('files', []):
                # print(file)
                print('|',
                      file.get('id'),
                      '|',
                      file.get('name'),
                      '|',
                      [(i.get('emailAddress'), i.get('displayName')) for i in file.get('owners')],
                      )
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                print('Nothing found')
                break

    def change_owner(self, doc_id=None):
        doc_id = doc_id or self.spreadsheetId
        # returns 'Permissions' dict
        permissions = self.service_v3.permissions().create(
            fileId=doc_id,
            transferOwnership=True,
            body={
                'type': 'user',
                'role': 'owner',
                'emailAddress': config.email,
            }
        ).execute()

        # Applies permission
        self.service_v3.files().update(
            fileId=doc_id,
            body={'permissionIds': [permissions['id']]}
        ).execute()

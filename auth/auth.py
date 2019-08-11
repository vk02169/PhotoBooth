import pickle
import logging
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import gdata
import gdata.photos.service
import gdata.media
import gdata.geo
import gdata.gauth
import webbrowser
import httplib2
from datetime import datetime, timedelta
from oauth2client.client import flow_from_clientsecrets

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/photoslibrary'
]


########################################################################################################################
# - Returns a handle to a DRIVE service
########################################################################################################################
def getDriveService(client_secrets_filename):
    authenticator = Authenticator(client_secrets_filename, "drive_saved_creds.pickle", "drive")
    return authenticator.getDriveService()


########################################################################################################################
# - Returns a handle to a PHOTOS service - Not working currently. Gives a 404 - not found GooglePhotosException
########################################################################################################################
def getPhotosService(client_secrets_filename):
    authenticator = Authenticator(client_secrets_filename, "photos_saved_creds.pickle", "photos")
    return authenticator.getPhotoService()


#######################################################################################################################
# Class: Authenticator
# Authenticates the application against Google Drive and saves the returned credentials onto a binary pickled file.
# There will be a one time web browser popup that will ask you to allow access to the desired email id.
#######################################################################################################################
class Authenticator:

    ###################################################################################################################
    # existsCredFile()
    # Checks if the pickled file is already available - in which case the web browser flow can be bypassed
    ###################################################################################################################
    def existsFile(self, pickle_filename):
        self.secrets_dir = os.environ["PHOTOBOOTH_HOME"] + "/secrets/"
        self.pickle_filepath = self.secrets_dir + pickle_filename
        return os.path.exists(self.pickle_filepath)

    ###################################################################################################################
    # constructor()
    # - Invokes the appropriate initializer depending upon the incoming marker ("drive" or "photos")
    ###################################################################################################################
    def __init__(self, client_secrets_filename, pickle_filename, marker):
        if marker == "photos":
            self.initAuthPhotos(client_secrets_filename, pickle_filename)
        else:
            self.initAuthDrive(client_secrets_filename, pickle_filename)

    ###################################################################################################################
    # initAuthDrive()
    # - Authenticates you against the GoogleDrive using the googleapiclient API. Unfortunately, this api is not supported
    # - for Google Photos, so we have to use alternate means. But the basic flow is the same.
    # - Checks if the pickled file is already available - in which case the web browser flow can be bypassed
    # - If there is no pickled file or credentials have expired (or if the SCOPES variable has changed since the last time),
    #   the web browser flow is invoked.
    #   The first time around, there is no pickled file available, and so the web browser authorization flow is invoked.
    ###################################################################################################################
    def initAuthDrive(self, client_secrets_filename, pickle_filename):
        logging.info(
            "Authenticator.initAuthDrive(): client_secrets=[%s], pickle_filename=[%s]" % (
                client_secrets_filename, pickle_filename))

        if self.existsFile(client_secrets_filename) == False:
            raise Exception("Authenticator.initAuthDrive(): Unable to find file: [%s]" % client_secrets_filename)

        # Check if we already logged in...if not the authentication flow will invoke a browser to authenticate
        # On a successful login, the cached credentials will be serialized into the cached_cred.pickle file
        self.pickled_credentials_drive = None
        if self.existsFile(pickle_filename):
            logging.info("Authenticator.initAuthDrive(): Found existing pickled file in [%s]" % (self.secrets_dir))
            file = open(self.pickle_filepath)
            self.pickled_credentials_drive = pickle.load(file)
            if (self.pickled_credentials_drive == None):
                raise Exception("Authenticator.initAuthDrive(): Unable to load pickled credentials from file")

            logging.info("Authenticator.initAuthDrive(): Loaded existing pickle file into object")

        # If first time ( i.e. cached_credentials are null), get new credentials. If not first time, but expired creds,
        # request a refresh.
        if not self.pickled_credentials_drive or not self.pickled_credentials_drive.valid:
            logging.info("Authenticator.initAuthDrive(): First time or pickled creds not valid")
            if self.pickled_credentials_drive and self.pickled_credentials_drive.expired and self.pickled_credentials_drive.refresh_token:  # Not first time, however, something wrong with creds...then need to refresh
                logging.info("Authenticator.initAuthDrive(): Refreshing token")
                self.pickled_credentials_drive.refresh(Request())
                logging.info("Authenticator.initAuthDrive(): Done refreshing token")
            else:
                logging.info("Authenticator.initAuthDrive(): Starting installed app flow...")
                flow = InstalledAppFlow.from_client_secrets_file(self.secrets_dir + client_secrets_filename, SCOPES)
                self.pickled_credentials_drive = flow.run_local_server(port=0)
                logging.info("Authenticator.initAuthDrive(): Back from installed app flow...")

            file = open(self.pickle_filepath, "wb")
            pickle.dump(self.pickled_credentials_drive,
                        file)  # Serialize credentials into client_secrets.pickle file
            logging.info("Authenticator.initAuthDrive(): Dumped credentials into [%s]" % (self.pickle_filepath))

            logging.info("Authenticator.initAuthDrive(): Returning!")

    ###################################################################################################################
    # initAuthPhotos()
    # - Authenticates you against the Google Photos using oauth2client API.
    # - Checks if the pickled file is already available - in which case the web browser flow can be bypassed
    # - If there is no pickled file or credentials have expired (or if the SCOPES variable has changed since the last time),
    #   the web browser flow is invoked.
    #   The first time around, there is no pickled file available, and so the web browser authorization flow is invoked.
    ###################################################################################################################
    def initAuthPhotos(self, client_secrets_filename, pickle_filename):
        logging.info(
            "Authenticator.initAuthPhotos(): Constructor for PHOTOS: client_secrets=[%s], pickle_filename=[%s]" % (
                client_secrets_filename, pickle_filename))

        if self.existsFile(client_secrets_filename) == False:
            raise Exception("Authenticator.initAuthPhotos(): Unable to find file: [%s]" % client_secrets_filename)

        # Check if we already logged in...if not the authentication flow will invoke a browser to authenticate
        # On a successful login, the cached credentials will be serialized into the cached_cred.pickle file
        self.pickled_credentials_photos = None
        if self.existsFile(pickle_filename):
            logging.info("Authenticator.initAuthPhotos(): Found existing pickled file in [%s]" % (self.secrets_dir))
            file = open(self.pickle_filepath)
            self.pickled_credentials_photos = pickle.load(file)
            if (self.pickled_credentials_photos == None):
                raise Exception("Authenticator.initAuthPhotos(): Unable to load pickled credentials from file")

            logging.info("Authenticator.initAuthPhotos(): Loaded existing pickle file into object")

        # If first time ( i.e. cached_credentials are null), get new credentials. If not first time, but expired creds,
        # request a refresh.
        if not self.pickled_credentials_photos or self.pickled_credentials_photos.invalid:
            logging.info("Authenticator.initAuthPhotos(): First time or pickled creds not valid")
            flow = flow_from_clientsecrets(self.secrets_dir + client_secrets_filename, scope=SCOPES,
                                           redirect_uri='urn:ietf:wg:oauth:2.0:oob')
            uri = flow.step1_get_authorize_url()
            webbrowser.open(uri)
            code = raw_input('Enter the authentication code: ').strip()
            self.pickled_credentials_photos = flow.step2_exchange(code)
            logging.info("Authenticator.initAuthPhotos(): Back from installed app flow...")

            if (
                    self.pickled_credentials_photos and self.pickled_credentials_photos.token_expiry - datetime.utcnow()) < timedelta(
                    minutes=5):
                logging.info("Authenticator.initAuthPhotos(): Refreshing token")
                http = httplib2.Http()
                http = self.pickled_credentials_photos.authorize(http)
                self.pickled_credentials_photos.refresh(http)
                logging.info("Authenticator.initAuthPhotos(): Done refreshing token")

            file = open(self.pickle_filepath, "wb")
            pickle.dump(self.pickled_credentials_photos, file)  # Serialize credentials into client_secrets.pickle file
            logging.info("Authenticator.initAuthPhotos(): Dumped credentials into [%s]" % (self.pickle_filepath))

            logging.info("Authenticator.initAuthPhotos(): Returning!")

    ###################################################################################################################
    # getDriveService()
    # Returns the drive service
    ###################################################################################################################
    def getDriveService(self):
        return build('drive', 'v3', credentials=self.pickled_credentials_drive)

    ###################################################################################################################
    # getPhotoService()
    # Returns the photo service. Note that is uses the gdata library and not the standard googleapiclient library.
    ###################################################################################################################
    def getPhotoService(self):
        user_agent = 'picasawebuploader'
        email = "vinayak.v.kumar@gmail.com"
        return gdata.photos.service.PhotosService(source=user_agent,
                                                  email=email,
                                                  additional_headers={
                                                      'Authorization': 'Bearer %s' % self.pickled_credentials_photos.access_token})


########################################################################################################################
# For testing only
########################################################################################################################
def main():
    os.environ["PHOTOBOOTH_HOME"] = "C:/Users/Behemoth/PycharmProjects/PhotoBooth2.0"
    testDrive()
    testPhotos()


def testPhotos():
    service = getPhotosService("client_secrets.json")
    albums = service.GetUserFeed(user='vinayak.v.kumar@gmail.com')
    for album in albums.entry:
        title = album.title.text
        title = ''.join([c for c in title if ord(c) < 128])
        id = album.gphoto_id.text
        print(u'{0} ({1})'.format(title, id))


def testDrive():
    # Call the Drive v3 API
    service = getDriveService("client_secrets.json")
    results = service.files().list(pageSize=30, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))


if __name__ == '__main__':
    main()
import pickle
import logging
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/drive']

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
        self.pickle_filepath= self.secrets_dir + pickle_filename
        return os.path.exists(self.pickle_filepath)

    ###################################################################################################################
    # constructor()
    # - Checks if the pickled file is already available - in which case the web browser flow can be bypassed
    # - If there is no pickled file or credentials have expired (or if the SCOPES variable has changed since the last time),
    #   the web browser flow is invoked.
    #   The first time around, there is no pickled file available, and so the web browser authorization flow is invoked.
    ###################################################################################################################
    def __init__(self, client_secrets_filename, pickle_filename):

        logging.info("Authenticator: __init__(): client_secrets=[%s], pickle_filename=[%s]"%(client_secrets_filename, pickle_filename))

        if self.existsFile(client_secrets_filename) == False:
            raise Exception ("Authenticator: __init__(): Unable to find file: [%s]"%client_secrets_filename)

        # Check if we already logged in...if not the authentication flow will invoke a browser to authenticate
        # On a successful login, the cached credentials will be serialized into the cached_cred.pickle file
        self.pickled_credentials = None
        if self.existsFile(pickle_filename):
            logging.info("Authenticator:__init__(): Found existing pickled file in [%s]"%(self.secrets_dir))
            file = open(self.pickle_filepath)
            self.pickled_credentials = pickle.load(file)
            if (self.pickled_credentials == None):
                raise Exception("Authenticator.__init__(): Unable to load pickled credentials from file")

            logging.info("Authenticator:__init__(): Loaded existing pickle file into object")

        # If first time ( i.e. cached_credentials are null), get new credentials. If not first time, but expired creds,
        # request a refresh.
        if not self.pickled_credentials or not self.pickled_credentials.valid:
            logging.info("Authenticator:__init__(): First time or pickled creds not valid")
            if self.pickled_credentials and self.pickled_credentials.expired and self.pickled_credentials.refresh_token: # Not first time, however, something wrong with creds...then need to refresh
                logging.info("Authenticator:__init__(): Refreshing token")
                self.pickled_credentials.refresh(Request())
                logging.info("Authenticator:__init__(): Done refreshing token")
            else:
                logging.info("Authenticator:__init__(): Starting installed app flow...")
                flow = InstalledAppFlow.from_client_secrets_file(self.secrets_dir + client_secrets_filename, SCOPES)
                self.pickled_credentials = flow.run_local_server(port=0)
                logging.info("Authenticator:__init__(): Back from installed app flow...")

            file = open(self.pickle_filepath, "wb")
            pickle.dump(self.pickled_credentials, file) # Serialize credentials into client_secrets.pickle file
            logging.info("Authenticator:__init__(): Dumped credentials into [%s]"%(self.pickle_filepath))

        logging.info("Authenticator:__init__(): Returning!")

    ###################################################################################################################
    # getDriveService()
    # Returns the drive service
    ###################################################################################################################
    def getDriveService(self):
        return build('drive', 'v3', credentials=self.pickled_credentials)

def main():
    os.environ["PHOTOBOOTH_HOME"]="C:/Users/Behemoth/PycharmProjects/PhotoBooth2.0"
    a = Authenticator("client_secrets.json", "client_secrets.pickle")
    service = a.getDriveService()
    listFiles(service)

def listFiles(service):
    # Call the Drive v3 API
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

from googleapiclient.http import MediaFileUpload
from thrmodel   import BackgroundProcessor
from camconfig          import Configurator
from auth import Authenticator

import logging
import os
import sys

##################################################################################################################################
# Class: GoogleDriveUploader
# Singleton object that abstracts uploading files to a GoogleDrive. The class extends the BackgroundProcessor to ensure that all
# uploading takes place in a background thread.
# Note that to successfully upload pictures to Google Drive, you need to do the following:
#   1. Logon to console.developers.google.com with the login id of the google account that owns the drive
#   2. Create a project
#   3. Enable APIs for the project
#       a. In this case the Drive API
#       b. Go to the OAUTH consent screen. Fill in the application name
#       c. Save credentials. This will generate a secrets file. Download that file to your application.
#          Usually called client_secretsXXX.json
#       d. Use the Authenticator class to get a handle to the DRIVE Python API and upload pictures
##################################################################################################################################
class GoogleDriveUploader(BackgroundProcessor):
    __instance__  = None

    @staticmethod
    def instance():
        if GoogleDriveUploader.__instance__ == None:
            GoogleDriveUploader()
        return GoogleDriveUploader.__instance__

    def __init__(self):

        logging.info("GoogleDriveUploader constructor: IN")

        if GoogleDriveUploader.__instance__ != None:
            raise Exception("GoogleDriveUploader is a Singleton! Please use 'instance()' to get an object.")
        else:
            super(GoogleDriveUploader, self).__init__()
            GoogleDriveUploader.__instance__ = self
            self.auth = Authenticator("client_secrets.json", "drive_saved_creds.pickle", "drive")
            self.drive_service = self.auth.getDriveService()

    def preWorkFunction(self, data_array):
        logging.info("GoogleDriveUploader.preWorkFunction()")
        return True

    ##################################################################################################################################
    # name - workFunction()
    # The guts of this class is in this method. Essentially uploads files in the incoming files_array to google drive.
    #   - From configuration, gets the name of folder to upload files to
    #   - Searches for the folder in GoogleDrive
    #   - Once found, uploads files to the folder
    ##################################################################################################################################
    def workFunction(self, files_array):
        logging.info("GoogleDriveUploader.workFunction()...")

        # Get name of folder to upload from configuration and...
        folder=Configurator.instance().getGoogleDriveUploadFolder()
        if folder == None:
            raise Exception("GoogleDriveUploader.workFunction(): Invalid Google Drive folder")

        # ...try to find the folder on google drive.
        upload_folder_id = self.findFolder(folder)
        if upload_folder_id == None:
            raise Exception("Invalid folder: [%s]. Please create this folder on the drive." % (folder))

        # Iterate and upload. Simple.
        for filepath in files_array:
            logging.info("GoogleDriveUploader.workFunction(): Uploading to folder: [%s], thefile: [%s]..." % (folder, filepath))
            self.upload(filepath, upload_folder_id)
            logging.info("GoogleDriveUploader.workFunction(): DONE with [%s]" % (filepath))

    ##################################################################################################################################


    ##################################################################################################################################
    # upload()
    # Uploads an incoming file to the folder specified
    # The incoming folder_id represents the folder into which the file must be uploaded
    ##################################################################################################################################
    def upload(self, thefile, folder_id):
        file_metadata = {
                            'name': thefile,
                            'parents': [folder_id]
                        }
        media = MediaFileUpload(thefile, mimetype='image/jpeg')
        thefile = self.drive_service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()


    ##################################################################################################################################
    # name - findFolder()
    # Iterate through the list of drive folders and find the one that represents the incoming folder name
    # return: Folder ID
    ##################################################################################################################################
    def findFolder(self, folder_name):
        page_token = None

        # Execute a query to look only for mimetype= 'folder'...
        while True:
            results = self.drive_service.files().list(q="mimeType='application/vnd.google-apps.folder'", # Look only for folders
                                                  spaces='drive',
                                                  fields='nextPageToken, files(id, name)',
                                                  pageToken=page_token).execute()

            #...and get the list of folders
            folder_list = results.get('files', [])
            for folder in folder_list: # Search for YOUR folder and...
                if folder.get('name') == folder_name:
                    id = folder.get('id')
                    print ("ID for Folder:[%s] is [%s]" %(folder_name, id))
                    return id #...return its ID

            page_token = results.get('nextPageToken', None)
            if page_token is None:
                break

##################################################################################################################################
# name - main()
# Standalone testing
##################################################################################################################################
def main():
    logfile = "gd.log"
    logging.basicConfig(filename=logfile,
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    os.environ["PHOTOBOOTH_HOME"] = "/home/pi/git/photobooth"
    dl = GoogleDriveUploader.instance()

    folder_id=dl.findFolder("RaspiTest")
    dl.upload("/home/pit/git/photobooth/picture.jpg", folder_id)

if __name__ == "__main__":
    main()

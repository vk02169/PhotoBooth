import logging
from pydrive.auth       import GoogleAuth
from pydrive.drive      import GoogleDrive
from backgroundupload   import BackgroundUploader
from camconfig          import Configurator


##################################################################################################################################
# Class: GoogleDriveUploader
# Singleton object that abstracts uploading files to a GoogleDrive. The class extends the BackgroundUploader to ensure that all
# uploading takes place in a background thread.
##################################################################################################################################
class GoogleDriveUploader (BackgroundUploader):

    __instance__ = None

    @staticmethod
    def instance():
        if GoogleDriveUploader.__instance__ == None:
            GoogleDriveUploader()
        return GoogleDriveUploader.__instance__
    
    def __init__(self):
        if GoogleDriveUploader.__instance__ != None:
            raise Exception("Configurator is a Singleton! Please use 'instance()' to get a Configurator object.")
        else:
            super(GoogleDriveUploader, self).__init__()
            GoogleDriveUploader.__instance__ = self
            self.gauth=GoogleAuth()
            self.gauth.LocalWebserverAuth()
            self.drive=GoogleDrive(self.gauth)

    def prepUpload(self, data_array):
        logging.info("GoogleDriveUploader.prepUpload()")
        return True

    ##################################################################################################################################
    # name - doUpload()
    # The guts of this class is in this method. Essentially uploads files in the incoming files_array to google drive.
    #   - From configuration, gets the name of folder to upload files to
    #   - Searches for the folder in GoogleDrive
    #   - Once found, uploads files to the folder
    ##################################################################################################################################
    def doUpload(self, files_array):
        logging.info("GoogleDriveUploader.doUpload()...")

        # Get name of folder to upload from configuration and...
        folder = Configurator.instance().getGoogleDriveUploadFolder()
        if folder == None:
            raise Exception ("GoogleDriveUploader.doUpload(): Invalid Google Drive folder")

        #...try to find the folder on google drive.
        upload_folder_id = None
        file_list = self.drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        for file in file_list:
            if file["title"] == folder: # Found folder to upload to...
                upload_folder_id = file["id"]
                break

        if upload_folder_id == None:
            raise Exception("Invalid folder: [%s]. Please create this folder on the drive." % (folder))

        # Iterate and upload. Simple.
        for infilepath in files_array:
            logging.info("GoogleDriveUploader.doUpload(): Uploading to folder: [%s], file: [%s]..." %(folder, infilepath))
            handle = self.drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": upload_folder_id}]})
            handle.SetContentFile(infilepath)
            handle.Upload()
            logging.info("GoogleDriveUploader.doUpload(): DONE with [%s]" %(infilepath))

    ##################################################################################################################################

def main():
    logfile = "gd.log"
    logging.basicConfig( filename=logfile,
                         level=logging.INFO,
                         format='%(asctime)s %(levelname)s %(message)s')

    dl=GoogleDriveUploader.instance()
    listar=[]
    listar.append("/home/pi/git/photobooth/scripts/googledriveuploader.py")
    dl.upload("NY-2018-2019", listar)

if __name__ == "__main__":
    main()

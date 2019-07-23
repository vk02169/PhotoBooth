import os
import os.path
import time
import logging
import httplib2
import credentials

from backgroundupload       import BackgroundUploader
from util                   import *
from camconfig              import Configurator
from googledriveuploader    import GoogleDriveUploader


   
class PicasaUploader(BackgroundUploader):
    
    __instance__= None

    @staticmethod
    def instance():
        if PicasaUploader.__instance__== None:
            PicasaUploader()
        return PicasaUploader.__instance__
    
    def __init__(self):
        if PicasaUploader.__instance__!= None:
            raise Exception ("'PicasaUploader' is a Singleton object! Please use the 'instance()' method to get a reference.")
        else:
            super(PicasaUploader, self).__init__()
            self.initGoogleSetup()
            PicasaUploader.__instance__= self

    def initGoogleSetup(self):

        if Configurator.instance().getIsUploadNeeded() == False:
            return
            
        self.is_successful_signin = True            
        try:
            
            print "Signing in to Google..."
            
            # Create a client class which will make HTTP requests with Google Docs server.
            configdir = os.path.expanduser('./')
            client_secrets = os.path.join(configdir, 'OpenSelfie.json')
            credential_store = os.path.join(configdir, 'credentials.dat')
            self.client = credentials.OAuth2Login(client_secrets, credential_store, credentials.username)
            
            logging.info("Successfully signed into Google!")
            
            print "Signed in"
            
        except KeyboardInterrupt as ki:
            printExceptionTrace("KeyboardInterrupt", ki)
            
        except Exception as e:
            printExceptionTrace ("Error signing into Google. Check credentials", e)
            self.is_successful_signin = False
            

    def doUpload(self, images_array):
    
        logging.info( "In PicasaUploader.doUpload():...")
        album = Configurator.instance().getGoogleAlbum()
        if  album == -1:
            logging.error("NO ALBUM ID present in configuration. Please select Google album using the configuration tool")
            return

        album_url ='/data/feed/api/user/%s/albumid/%s' % (credentials.username, album)
        logging.info("PicasaUploader.doUpload(): Uploading to album. URL = [%s]" %(album_url))
        
        i=0
        while i < len(images_array):
            imgfile=images_array[i]
            s= "PicasaUploader.doUpload(): Uploading image file: [%s]..." % (imgfile)
            logging.info(s)
            self.client.InsertPhotoSimple(album_url,'VKSnap', "", imgfile ,content_type='image/jpeg')
            s = "PicasaUploader.doUpload(): DONE with [%s]..." %(imgfile)
            logging.info(s)
            i=i+1
            
    def prepUpload(self, images_array):

        logging.info("In PicasaUploader.prepUpload()...")
        if self.is_successful_signin:
            if Configurator.instance().getGoogleAlbum() == -1:
                logging.info("Need for first select an album. Select album using the 'Configure' button")
                logging.error("NOTHING Uploaded!")
            else:
                return True
        else:
            logging.info("There was no successful signin! Please perform the necessary setups")
            return False


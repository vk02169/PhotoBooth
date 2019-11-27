#from picasauploader         import PicasaUploader
from googledriveuploader    import GoogleDriveUploader
from camconfig              import Configurator
import logging

#Globals - these are singletons in any case.
picasa_uploader=None
drive_uploader=None

###############################################################################
# name - uploadImages() - Upload images to various locations
# Check configuration for upload to picasa and google drive. Only upload to them
# if configuration says so.
###############################################################################
def uploadImages(picsarray):

    global picasa_uploader, drive_uploader

    config= Configurator.instance()
    if config.isUploadToPicasa():
        logging.info("Uploading to Picasa...")
 #       if picasa_uploader == None:
  #          picasa_uploader = PicasaUploader.instance()
   #     picasa_uploader.kickOff(picsarray)
    else:
        logging.info("Upload to Picasa OFF in configuration")

    if config.isUploadToDrive():
        logging.info("Uploading to Google Drive...")
        if drive_uploader == None:
            drive_uploader = GoogleDriveUploader.instance()
        drive_uploader.kickOff(picsarray)
    else:
        logging.info("Upload to Google OFF in configuration")

###############################################################################
# cleanupLoaders() - Allow for graceful shutdown of background threads
###############################################################################
def cleanupUploaders():
    if picasa_uploader != None:
        picasa_uploader.cleanup()
    if drive_uploader != None:
        drive_uploader.cleanup()


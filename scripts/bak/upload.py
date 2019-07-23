from picasauploader         import PicasaUploader
from googledriveuploader    import GoogleDriveUploader
from camconfig              import Configurator

#Globals
picasa_uploader=None
drive_uploader=None

###############################################################################
# uploadImages() - Upload images to various locations
###############################################################################
def uploadImages(picsarray):

    global picasa_uploader, drive_uploader

    config= Configurator.instance()
    if config.isUploadToPicasa():
        picasa_uploader = PicasaUploader.instance()
        picasa_uploader.upload(picsarray)

    if config.isUploadToDrive():
        drive_uploader = GoogleDriveUploader.instance()
        drive_uploader.upload(picsarray)

###############################################################################
# cleanupLoaders() - Allow for graceful shutdown of background threads
###############################################################################
def cleanupUploaders():
    if picasa_uploader != None:
        PicasaUploader.instance().cleanup()
    if drive_uploader != None:
        GoogleDriveUploader.instance().cleanup()
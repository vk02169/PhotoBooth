
import logging

from util       import *
from camconfig  import Configurator
from picamera   import PiCamera

##################################################################################################################################
# name - getCamera()
# A Camera access method - instantiates the BoothCamera object and returns it.
##################################################################################################################################

def getCamera():
    return BoothCamera.instance()

##################################################################################################################################

##################################################################################################################################
# class BoothCamera - extends the PiCamera class. Sets some default values 
# for resolution and size of preview window, its opacity etc.
##################################################################################################################################

class BoothCamera (PiCamera):

    __instance__ = None

    @staticmethod
    def instance():
        if BoothCamera.__instance__ is None:
            BoothCamera()
        return BoothCamera.__instance__

    def __init__(self):
        if BoothCamera.__instance__ is not None:
            raise Exception ("BoothCamera is a Singleton! Try using the 'instance()' method.")
        BoothCamera.__instance__ = self

        super(BoothCamera, self).__init__()
        config = Configurator.instance()
        self.resolution=config.getResolution()        # Resolution of preview as well as capture
        self.preview_alpha = config.getPreviewAlpha() # Opacity of the preview screen
        self.preview_fullscreen = False
        self.preview_window=(0, 40, config.getScreenWidth(), config.getScreenHeight()-150)
        self.iso = config.getISO()
        self.sharpness = config.getSharpness()

        
    def capture(self, imagefilename):
        config = Configurator.instance()
        logging.info("In BoothCamera.capture(): resolution= %s, ISO=%d, sharpness=%s" % (str(self.resolution), self.iso, self.sharpness) )
        return super(BoothCamera, self).capture(imagefilename)

    def start_preview(self):
        super(BoothCamera, self).start_preview()
        
    def stop_preview(self):
        super(BoothCamera, self).stop_preview()

    def close(self):
        super(BoothCamera, self).close()

    ##################################################################################################################################
    # name - snap()
    # - Given an incoming camera object - uses it to snap a picture and...
    # - ...saves it to the file: 'imagefile' as defined in configuration.
    # - Once the file is saved, archives it to the archive directory (and changes the filename to a new file name in the process)
    ##################################################################################################################################
    def snap(self):
        try:
            config = Configurator.instance();
            imagefile = config.getDefaultImageFilename()
            self.capture(imagefile)
            new_filename = archiveImage(imagefile)
            return new_filename

        except Exception as e:
            printExceptionTrace("BoothCamera.snap(): exception! ", e)
            new_filename = None

        return new_filename
        
    		
##################################################################################################################################


    

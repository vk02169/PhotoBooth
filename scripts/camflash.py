import RPi.GPIO as GPIO
from camconfig import Configurator

##################################################################################################################################
# CameraFlash
# A singleton class that manages all flash related constructs, including reading the configuration to check if flash is configured
# to be ON or not.
##################################################################################################################################s
class CameraFlash (object):

    __instance__ = None

    ###############################################################################################################################
    # instance()
    # Ensures a singleton object
    ###############################################################################################################################
    @staticmethod
    def instance():
        if CameraFlash.__instance__ == None:
            CameraFlash()
        return CameraFlash.__instance__

    ###############################################################################################################################
    # __init__()
    # Constructor that ensures a singleton. Initializes some of the GPIO settings from configuration.
    ###############################################################################################################################
    def __init__(self):
        if CameraFlash.__instance__ != None:
            raise Exception("CameraFlash is a Singleton! Please use 'instance()' to get an object.")
        CameraFlash.__instance__=self
        self.gpio_pin = Configurator.instance().getFlashGPIOAssignment()



    ###############################################################################################################################
    # fireFlash()
    # API to turn on flash. Basically just turns the GPIO pin (that was configured to be the flash trigger pin) to HIGH.
    ###############################################################################################################################
    def fireFlash(self):
        config = Configurator.instance()

        # If flash is configured to be ON...
        if config.getFlashDisposition():
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.gpio_pin, GPIO.OUT)
            #...then set the appropriate GPIO pin to HIGH
            GPIO.output(self.gpio_pin, GPIO.HIGH)

    ###############################################################################################################################
    # flashOff()
    # API to turn off flash. Basically just turns the GPIO pin (that was configured to be the flash trigger pin) to LOW.
    ###############################################################################################################################
    def flashOff(self):
        config = Configurator.instance()

        # If flash is configured to be ON...
        if config.getFlashDisposition():
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.gpio_pin, GPIO.OUT)
            # ...then set the appropriate GPIO pin to LOWs
            GPIO.output(self.gpio_pin, GPIO.LOW)
            GPIO.cleanup()



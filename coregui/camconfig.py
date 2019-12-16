#
#  
import configparser
import os
import tkinter
import tkinter.filedialog
import logging


##################################################################################################################################
# Configurator 
# A singleton class that manages all configuration for the application.
# It also provides with a rudimentary dialog box to change and save configuration items.
# The class is imlemented as a Singleton
##################################################################################################################################
class Configurator(object):

    # The single instance
    __instance = None
   
    @staticmethod 
    def instance():
        if Configurator.__instance == None:
            Configurator()
        return Configurator.__instance
        
    
    conf_filename = "vkphotobooth.conf"

    CONF_FUN_SECTION = "FUN_STUFF"
    FUN_CMD = "fun_cmd"

    # Various configuration options
    CONF_PHOTO_SECTION  = "PHOTO"
    OPTION_COUNTDOWN_TEXT = "countdown_text"
    OPTION_NUMPICS = "num_pics"
    OPTION_ARCHIVE_DIR  = "archive_dir"
    OPTION_MOD_BASE     = "modulo_base"
    OPTION_WIDTH        = "screen_width"
    OPTION_HEIGHT       = "screen_height"
    OPTION_SHOW_BUTTONS = "show_exit_configure_btns"
        
    CONF_CAMERA_SECTION = "CAMERA_ATTRIBUTES"
    OPTION_RESX = "res_pixels_X"
    OPTION_RESY = "res_pixels_Y"
    OPTION_BASE_IMG_EXT = "base_image_ext"
    OPTION_PREVIEW_ALPHA = "preview_alpha"
    OPTION_ISO       = "iso"
    OPTION_SHARPNESS = "sharpness"

    CONF_FLASH_SECTION      = "FLASH_ATTRIBUTES"
    OPTION_FLASH            = "is_flash_on"
    OPTION_FLASH_GPIO_PIN   = "gpio_pin"
    OPTION_FLASH_ON_TIME   =  "flash_on_time"

    CONF_UPLOAD_SECTION = "UPLOAD_TO_GCP"
    OPTION_IS_UPLOAD_NEEDED     ="is_upload_needed"
    OPTION_ALBUMID              = "album_id"
    OPTION_GOOGLE_ACCT          = "google_account"
    OPTION_DRIVE_FOLDER         ="google_drive_upload_folder"
    OPTION_UPLOAD_TO_DRIVE      = "is_upload_to_drive"
    OPTION_UPLOAD_TO_PICASA     = "is_upload_to_picasa"

  
    ######################################################    
    # Bindings to instance variables for widgets
    #

    def bindCountdown(self, strvar, widget):
        self.countdown_text = strvar.get()
        
    def bindNumPics(self, strvar, widget):
        s = strvar.get()
        if s is not '':
            self.num_pics = int(s)
        
    def bindResX(self, strvar, widget):
        s = strvar.get()
        if s is not '':
            self.resX = int(s)
        
    def bindResY(self, strvar, widget):
        s = strvar.get()
        if s is not '':
            self.resY = int(s.get())
        
    def bindBaseImageExt(self, strvar, widget):
        self.base_image_ext=strvar.get()
        
    def bindAlbum(self, strvar, widget):
        s = strvar.get()
        if s is not '':
            self.google_photos_album = int(s)
        
    def bindArchive(self, strvar, widget):
        self.pics_archive_dir = strvar.get()

    def bindGoogleAcct(self, strvar, widget):
        self.google_acct = strvar.get()
        
    def bindPreviewAlpha(self, strvar, widget):
        s = strvar.get()
        if s is not '':     
            self.preview_alpha = int(s)

    ##################################################################################################################################
    # onSave()
    # Save config changes to the prescribed configuration file.
    ##################################################################################################################################
    def onSave(self, *args):
        conf = configparser.ConfigParser()
        conf.add_section(self.CONF_PHOTO_SECTION)
        conf.set(self.CONF_PHOTO_SECTION, self.OPTION_COUNTDOWN_TEXT,       self.countdown_text)
        conf.set(self.CONF_PHOTO_SECTION, self.OPTION_NUMPICS,              str(self.num_pics))
        conf.set(self.CONF_PHOTO_SECTION, self.OPTION_ARCHIVE_DIR,          self.pics_archive_dir)
        conf.set(self.CONF_PHOTO_SECTION, self.OPTION_MOD_BASE,             str(self.mod_base))
        conf.set(self.CONF_PHOTO_SECTION, self.OPTION_WIDTH,                str(self.screen_width))
        conf.set(self.CONF_PHOTO_SECTION, self.OPTION_HEIGHT,               str(self.screen_height))
        conf.set(self.CONF_PHOTO_SECTION, self.OPTION_SHOW_BUTTONS,         str(self.show_exit_configure_btns))

        conf.add_section(self.CONF_CAMERA_SECTION)
        conf.set(self.CONF_CAMERA_SECTION, self.OPTION_RESX,            str(self.resX))
        conf.set(self.CONF_CAMERA_SECTION, self.OPTION_RESY,            str(self.resY))
        conf.set(self.CONF_CAMERA_SECTION, self.OPTION_BASE_IMG_EXT,    self.base_image_ext)
        conf.set(self.CONF_CAMERA_SECTION, self.OPTION_PREVIEW_ALPHA,   str(self.preview_alpha))
        conf.set(self.CONF_CAMERA_SECTION, self.OPTION_ISO,             str(self.iso))
        conf.set(self.CONF_CAMERA_SECTION, self.OPTION_SHARPNESS,       str(self.sharpness))

        conf.add_section(self.CONF_FLASH_SECTION)
        conf.set(self.CONF_FLASH_SECTION, self.OPTION_FLASH,          str(self.is_flash_on))
        conf.set(self.CONF_FLASH_SECTION, self.OPTION_FLASH_GPIO_PIN,  str(self.gpio_pin))
        conf.set(self.CONF_FLASH_SECTION, self.OPTION_FLASH_ON_TIME,  str(self.flash_on_time))

        conf.add_section(self.CONF_UPLOAD_SECTION)
        conf.set(self.CONF_UPLOAD_SECTION, self.OPTION_ALBUMID,             str(self.google_photos_album))
        conf.set(self.CONF_UPLOAD_SECTION, self.OPTION_IS_UPLOAD_NEEDED,    str(self.is_upload_needed))
        conf.set(self.CONF_UPLOAD_SECTION, self.OPTION_GOOGLE_ACCT,         self.google_acct)
        conf.set(self.CONF_UPLOAD_SECTION, self.OPTION_DRIVE_FOLDER,        self.drive_folder)
        conf.set(self.CONF_UPLOAD_SECTION, self.OPTION_UPLOAD_TO_DRIVE,     str(self.is_upload_to_drive))
        conf.set(self.CONF_UPLOAD_SECTION, self.OPTION_UPLOAD_TO_PICASA,    str(self.is_upload_to_picasa))

        conf_filename = self.getCompleteConfFilename()
        f = open(conf_filename, 'w')
        conf.write(f)
        print ("Configfile written successfully! [%s]" %(f.name))
        self.top.destroy()
        
    def onCancel(self, *args):
        self.top.destroy()
       
    ##################################################################################################################################
    #  name: displayConfigUI - This is the main dialog box for configuration management.
    #  @param
    #  @return
    ##################################################################################################################################
    def displayConfigUI(self, main_win):
        self.top = tkinter.Toplevel(main_win)
       
        self.main_win = main_win        
        self.top.wm_title("Manage Configuration")
        
        self.top.grab_set()
        self.top.transient(main_win)
        
        self.drawTextEntry( self.top,    "Countdown", str(self.countdown_text),      self.bindCountdown, 10)
        self.drawTextEntry( self.top,    "Num pics",  str(self.num_pics),       self.bindNumPics, 10 )
       
        self.drawTextEntry( self.top,    "ResX",  str(self.resX),               self.bindResX, 10)
        self.drawTextEntry( self.top,    "ResY",  str(self.resY),               self.bindResY, 10 )
        self.drawTextEntry( self.top,    "Image type",  self.base_image_ext,    self.bindBaseImageExt, 10)
        self.drawTextEntry( self.top,    "Preview alpha",  self.preview_alpha,  self.bindPreviewAlpha, 10)
 
        self.drawTextEntry( self.top,    "Google acct",  self.google_acct,    self.bindGoogleAcct, 30)
        frame, album_entry=self.drawTextEntry( self.top,    "Google album",  str(self.google_photos_album), self.bindAlbum, 15 )
        tkinter.Button(frame, text="Lookup...", command=lambda: self.onLookup(album_entry)).pack();

        self.drawFileBrowse(self.top,    "Archive dir",  self.pics_archive_dir,        self.bindArchive, 20, False )

        buttonbox = tkinter.Frame(self.top)
        tkinter.Button(buttonbox, text= "Save",   command=self.onSave).pack(side=tkinter.LEFT)
        tkinter.Button(buttonbox, text= "Cancel", command=self.onCancel).pack(side=tkinter.RIGHT)
        buttonbox.pack()

    def onLookup(self, album_entry):
        logging.info("Calling listalbums with google_acct: [%s]"%self.google_acct)
     #   self.albums = listalbums.getAlbums(self.google_acct)
     #   listalbums.AlbumSelect(self.top, album_entry, self.albums)

    #        
    #  name: drawCheckBox
    #  @param
    #  @return
    #  
    def drawCheckBox(self, top, label, initial_val, listener):
        frame = tkinter.Frame(top)
        var = tkinter.BooleanVar()
        var.set(initial_val)
        checkbox = tkinter.Checkbutton(self, text=label, variable=var)
        var.trace('w', lambda *args:listener(var, checkbox))
        checkbox.pack()
        frame.pack()            
        
    def drawFileBrowse(self, top, label, initial_val, listener, w, is_browse_file):
        frame = tkinter.Frame(top)
        var = tkinter.StringVar()
        var.set(initial_val)
        tkinter.Label(frame, text=label).pack(padx=5, pady=5, side=tkinter.LEFT)
        entry = tkinter.Entry(frame, textvariable=var, width=w)
        entry.pack(padx=5, pady=5, side=tkinter.LEFT)
        var.trace('w', lambda * args: listener(var, entry))
        tkinter.Button(frame, text='Browse', command=lambda: self.drawArchiveDialog(var, is_browse_file)).pack(side=tkinter.LEFT)
        frame.pack(side=tkinter.TOP)

    ##################################################################################################################################
    #  name: drawArchiveDialog
    #  Displays the file dialog with selection params
    ##################################################################################################################################
    def drawArchiveDialog(self, var_to_update, is_browse_file):
        options = {}
        options['initialdir'] = '/media'
        options['parent'] = self.top
        
        if not is_browse_file:
            options['title'] = 'Select Archive Directory'
            output = tkFileDialog.askdirectory(**options)
        else:
            options['title'] = 'Select File'
            output = tkFileDialog.askopenfilename(**options)

        var_to_update.set(output)
        
                
    ##################################################################################################################################
    #  name: Configurator.drawTextEntry
    #  Utility method to create a text entry widget and register the incoming listener to it.
    ##################################################################################################################################
    def drawTextEntry(self, top, label, initial_val, listener, w):
        frame = tkinter.Frame(top)
        var =   tkinter.StringVar()
        var.set(initial_val)
        tkinter.Label(frame, text=label).pack(padx=5, pady=5, side=tkinter.LEFT)
        entry = tkinter.Entry(frame, textvariable=var, width=w)
        entry.pack(padx=5, pady=5, side=tkinter.RIGHT)
        var.trace('w', lambda *args:listener(var, entry))
        frame.pack()
        return frame, entry

    ##################################################################################################################################
    #  name: setConfigDefaults - sets default configuration parameters. Stores them in instance variables
    #  @param - none
    #  @return - none
    ##################################################################################################################################
    def setConfigDefaults(self):
        self.fun_cmd = ""
        self.google_photos_album=-1
        self.countdown_text = "Smile!"
        self.num_pics = 4
        self.base_image_filename = "picture"
        self.pics_archive_dir=self.install_dir + "/archived_pics/"
        self.base_image_ext="jpg"
        self.resX = 3280
        self.resY = 2464
        self.preview_alpha = 100
        self.mod_base = 1540333116
        self.is_upload_needed = True
        self.google_acct = "vinayak.v.kumar@gmail.com"
        self.iso = 400
        self.sharpness=50
        self.screen_width  = 800  # for the 7" touch screen
        self.screen_height = 480
        self.drive_folder="NY-2018-2019"
        self.is_upload_to_drive=True
        self.is_upload_to_picasa=True
        self.show_exit_configure_btns=False
        self.is_flash_on=True
        self.flash_on_time=2
        self.gpio_pin = 7

    ##################################################################################################################################
    #  name: loadConfFromFile - loads configuration settings from configuration file (vkphotobooth.conf by default)
    ##################################################################################################################################
    def loadConfFromFile(self):
        try:
            print ("loadConfFromFile(): Reading from: [%s]" % (self.getCompleteConfFilename()))
            
            self.setConfigDefaults()

            conf = configparser.ConfigParser();
            conf.read(self.getCompleteConfFilename())
            
            readstream = conf.read(self.getCompleteConfFilename())
            if readstream == []:
                raise IOError ("Unable to find configuration file: " +      self.getCompleteConfFilename())

            self.fun_cmd = conf.get(self.CONF_FUN_SECTION, self.FUN_CMD)

            self.countdown_text      = conf.get(self.CONF_PHOTO_SECTION,            self.OPTION_COUNTDOWN_TEXT)
            self.num_pics           = int(conf.get(self.CONF_PHOTO_SECTION,         self.OPTION_NUMPICS))
            self.pics_archive_dir   =   conf.get(self.CONF_PHOTO_SECTION,           self.OPTION_ARCHIVE_DIR)
            self.mod_base    =   int(conf.get(self.CONF_PHOTO_SECTION,              self.OPTION_MOD_BASE))
            self.screen_width    =   int(conf.get(self.CONF_PHOTO_SECTION,          self.OPTION_WIDTH))
            self.screen_height   =   int(conf.get(self.CONF_PHOTO_SECTION,          self.OPTION_HEIGHT))
            s=conf.get(self.CONF_PHOTO_SECTION,  self.OPTION_SHOW_BUTTONS)
            self.show_exit_configure_btns= (s.lower() == "True".lower())

            self.resX            = int(conf.get(self.CONF_CAMERA_SECTION,   self.OPTION_RESX))
            self.resY            = int(conf.get(self.CONF_CAMERA_SECTION,   self.OPTION_RESY))
            self.base_image_ext  = conf.get(self.CONF_CAMERA_SECTION,       self.OPTION_BASE_IMG_EXT)
            self.preview_alpha   = int(conf.get(self.CONF_CAMERA_SECTION,   self.OPTION_PREVIEW_ALPHA))
            self.iso             = int(conf.get(self.CONF_CAMERA_SECTION,   self.OPTION_ISO))
            self.sharpness       = int(conf.get(self.CONF_CAMERA_SECTION,   self.OPTION_SHARPNESS))

            s                    = conf.get(self.CONF_FLASH_SECTION,       self.OPTION_FLASH)
            self.is_flash_on         = (s.lower() == "True".lower())
            self.flash_on_time   = int(conf.get(self.CONF_FLASH_SECTION,   self.OPTION_FLASH_ON_TIME))
            self.gpio_pin        = int(conf.get(self.CONF_FLASH_SECTION,   self.OPTION_FLASH_GPIO_PIN))

            self.google_photos_album    = int(conf.get(self.CONF_UPLOAD_SECTION,        self.OPTION_ALBUMID))
            self.is_upload_needed       = bool(conf.get(self.CONF_UPLOAD_SECTION,       self.OPTION_IS_UPLOAD_NEEDED))
            self.google_acct            = conf.get(self.CONF_UPLOAD_SECTION,            self.OPTION_GOOGLE_ACCT)
            self.drive_folder           = conf.get(self.CONF_UPLOAD_SECTION,            self.OPTION_DRIVE_FOLDER)
            s = conf.get(self.CONF_UPLOAD_SECTION,    self.OPTION_UPLOAD_TO_DRIVE)
            self.is_upload_to_drive = (s.lower() == "True".lower())
            s = conf.get(self.CONF_UPLOAD_SECTION, self.OPTION_UPLOAD_TO_PICASA)
            self.is_upload_to_picasa = (s.lower() == "True".lower())


        except (configparser.Error, err):
            print("loadConfFromFile(): ConfigParser exception! " + err)
            
        except (IOError, err):
            print ("loadConfFromFile(): IOError exception!" + err)

    ##################################################################################################################################
    # Constructor - implements the singleton pattern
    ##################################################################################################################################
    def __init__(self):
        if Configurator.__instance != None:
            raise Exception ("Configurator is a Singleton! Please use 'instance()' to get a Configurator object.")
        else:
            Configurator.__instance = self
            self.install_dir = os.environ["PHOTOBOOTH_HOME"]
            print ("Install directory is: [%s]"%self.install_dir)
            self.loadConfFromFile();

    ##################################################################################################################################

    ##################################################################################################################################
    # Various gettor methods
    ##################################################################################################################################
    def getFunCMD(self):
        return self.fun_cmd

    def getDefaultImageFilename(self):
        return "picture." + self.base_image_ext
   
    def getArchiveFolder(self):
        return self.pics_archive_dir

    def getCompleteConfFilename(self):
        return self.install_dir + "/conf/" + self.conf_filename
        
    def getInstallDir(self):
        return self.install_dir

    def getResolution(self):
        return (self.resX, self.resY);

    def getBaseImageExt(self):
        return self.base_image_ext
        
    def getCountdownText(self):
        return self.countdown_text
        
    def getNumPics(self):
        return self.num_pics
        
    def getGoogleAlbum(self):
        return self.google_photos_album
    
    def getIsUploadNeeded(self):
        return self.is_upload_needed

    def getGoogleDriveUploadFolder(self):
        return self.drive_folder
        
    def getModuloBaseline(self):
        return self.mod_base

    def getPreviewAlpha(self):
        return self.preview_alpha
        
    def getISO(self):
        return self.iso
        
    def getSharpness(self):
        return self.sharpness
        
    def getScreenWidth(self):
        return self.screen_width
        
    def getScreenHeight(self):
        return self.screen_height

    def isUploadToDrive(self):
        return self.is_upload_to_drive

    def isUploadToPicasa(self):
        return self.is_upload_to_picasa

    def showExitConfigureBtns(self):
        return self.show_exit_configure_btns

    def getFlashDisposition(self):
        return self.is_flash_on

    def getFlashGPIOAssignment(self):
        return self.gpio_pin

    def getFlashOnTime(self):
        return self.flash_on_time

    ##################################################################################################################################
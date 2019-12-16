
##################################################################################################################################
# The original photobooth application was written by WYLUM. I have borrowed from their code base and the proceeded to enhance/subtract.
# Especially the part where the application uploads to Google Picasa, the code within listalbums.py and credentials.py remains
# unchanged from the original. As does tkkb.py. I claim no credit for it.
##################################################################################################################################

#Imports
import time
import tkinter.messagebox
import logging
import PIL
import sys

from PIL            import ImageTk
from tkinter        import *

from corecam        import getCamera
from corecam        import BoothCamera
import camconfig
from util           import *

from upload import uploadImages
from upload import cleanupUploaders

##################################################################################################################################
# Constants and Globals
##################################################################################################################################
BASE_TN_X_COORD = 120
BASE_TN_Y_COORD = 10
IMG_BORDER_PIXELS = 5
CANVAS_TEXT_FONT = ("Helvetica", 38, 'bold')
TEXT_HEIGHT_OFFSET = 204
img_to_disp_array=[]

##################################################################################################################################
# name: displayImage(imgfile, i)
# Displays a thumbnail of the incoming image onto a (grid location) specified by
# the parameter 'i'
##################################################################################################################################
def displayImage(imgfile, i):

    logging.info("In displayImage():...")

    img = PIL.Image.open(imgfile)

    #Create thumbnail of incoming image
    img.thumbnail(MAX_TN_SIZE, PIL.Image.ANTIALIAS)

    #Calculate coordinates of where to display thumbnail...
    tn_size = img.size

    x = BASE_TN_X_COORD + (i%2) * (tn_size[0] + IMG_BORDER_PIXELS)

    if (i%2 == 1):
        i=i-1
    y = BASE_TN_Y_COORD + (i/2) * (tn_size[1] + IMG_BORDER_PIXELS)
    
    
    #...and format it to a displayable format.
    global img_to_disp_array
    
    img_to_disp = ImageTk.PhotoImage(img)
    img_to_disp_array.append(img_to_disp) #To keep reference alive
    
    # Finally, display the thumbnail at appropriate locations
    img_display_canvas.create_image([x, y], image=img_to_disp, tags="image", anchor=NW)
    img_display_canvas.update()
    
    logging.info("Exiting displayImage()")
##################################################################################################################################

##################################################################################################################################
# name: displayImages(picsarray)
# Receives an array of imagefiles in the incoming parameter.
# -for each imagefile
#       -invokes the displayImage() method to display image appropriately
##################################################################################################################################
def displayImages(picsarray):
    i=0
    img_to_disp_array=[] # Reset results of prior thumbnail display
    while i < len(picsarray):
        imgfile = picsarray[i]
        displayImage(imgfile, i)
        i=i+1


##################################################################################################################################
# name: startCountdown()
# Needs the incoming camera argument to start the whole preview process.
# Displays the countdown text one letter at a time (using the CountdownText
# utility class. Stops preview once countdown is completed.
##################################################################################################################################
def startCountdown(camera, canvas, countdown_text="Smile!"):

    clearCanvas(canvas, "all")
 
    logging.info("Calling CountdownText()...")
    
    CountdownText(text=countdown_text,
                  font=CANVAS_TEXT_FONT,
                  canvas=canvas,
                  fill="purple",
                  x=WIDTH/2, 
                  y=HEIGHT/2+TEXT_HEIGHT_OFFSET,
                  anchor=tkinter.CENTER)
                  
    logging.info("Back from CountdownText()")
    clearCanvas(canvas, "text")

##################################################################################################################################
#  name: startBooth()
#  Kicks off the capture process:
#       -for each picture to be taken
#               -starts countdown.
#               -snaps the picture (which automatically archives the pictures locally)
#       -once all pictures are snapped, displays them in a grid on the canvas.
#       -finally uploads these pictures to external cloud(s)
#  @param
#  @return
##################################################################################################################################
def startBooth():

    # Prevent against race condition issues
    global is_booth_in_progress
    if is_booth_in_progress:
        return
    is_booth_in_progress = True
    
    logging.info("In startBooth()...")

    num_pics  = config.getNumPics()
    if num_pics > 4: #capping off the number of pictures (within a selfie) to 4 irrespective of configuration
        num_pics = 4
    i=0

    global picsarray
    picsarray=[] #reset

    global funpicsarray
    funpicsarray=[] #reset

    try:
        camera = getCamera()
        clearCanvas(img_display_canvas)

        camera.start_preview()
        time.sleep(2)  # Camera warm up time

        # Capture the pics first. 
        # For each pic...
        while i < num_pics:
        
            #...get ready for (next) picture in the session.
            BlinkingText(text="Get ready!",
                            font=CANVAS_TEXT_FONT,
                            fill="purple",
                            blink_freq=.5,
                            num_blinks=3,
                            canvas=img_display_canvas,
                            x=WIDTH/2, y=HEIGHT/2+TEXT_HEIGHT_OFFSET,
                            anchor=tkinter.CENTER)

        
            #Count it down and...
            startCountdown(camera, img_display_canvas, countdown_text=config.getCountdownText())

            #...snap the picture. Add it to the list of images and then...
            new_filename, fun_filename = camera.snap()
            funpicsarray.append(fun_filename)
            picsarray.append( new_filename )
            if picsarray[i] is None:
                messageBox("Error", "Error", "No pictures were taken!")
                break
            clearCanvas(img_display_canvas);
            i=i+1
            ## End while
        

        clearCanvas(img_display_canvas, "all");
        camera.stop_preview()

        # ...display and...
        displayImages(picsarray)
        # ...upload
        uploadImages(picsarray)
        time.sleep(5) # Arbitrary time to allow people to view thumbnail(s)

        #Do the same with the FX pics
        displayImages(funpicsarray)
        uploadImages(funpicsarray)
        time.sleep(5) # Arbitrary time to allow people to view thumbnail(s)

        clearCanvas(img_display_canvas, "all");       
        logging.info("Exiting startBooth()")


    except Exception as e:
        printExceptionTrace("In startBooth()!", e)
        
    finally:
        is_booth_in_progress=False
        splashText()


##################################################################################################################################
# onClose() - Called in response to the Exit button
##################################################################################################################################
def onClose(*args, **kw):
    if is_booth_in_progress:
        return
    if main_win.after_id is not None:
       main_win.after_cancel(main_win.after_id)
    logging.info("onClose(): Cleaning up uploaders...")
    cleanupUploaders()
    getCamera().close()
    main_win.quit()
##################################################################################################################################



##################################################################################################################################
# name - configure()
# Bring up the Configurator UI to maintain configurations
##################################################################################################################################
def configure(main_win):
    configurator=Configurator.instance()
    configurator.displayConfigUI(main_win)
#################################################################


##################################################################################################################################
# onClick()
# This method is called in response to a mouse click or a touch on the
# touch screen.
##################################################################################################################################

def onClick(*args):
    startBooth()
    
##################################################################################################################################


##################################################################################################################################
# displaySplashButton()
# Utility method to paint the "Click!" button icon onto the canvas
##################################################################################################################################
def displaySplashButton():

    basedir = Configurator.instance().getInstallDir()
    img = PIL.Image.open(basedir+"/coreimgs/press.png")

    # Create thumbnail of the button image
    img.thumbnail(MAX_TN_SIZE, PIL.Image.ANTIALIAS)
    tn_size=img.size

    x = WIDTH/2 -  tn_size[0]/2
    y = HEIGHT/2 - tn_size[1]/2 -20

    # ...and format it to a displayable format.
    global click_btn_img_to_disp

    click_btn_img_to_disp = ImageTk.PhotoImage(img)

    # Finally, display the thumbnail at appropriate locations
    img_display_canvas.create_image([x, y], image=click_btn_img_to_disp, tags="image", anchor=NW)
    img_display_canvas.update()

def rgbToColor(rgb):
    return "#%02x%02x%02x" % rgb

def splashText():
    img_display_canvas.config(background=rgbToColor((255,128,64)))
    displaySplashButton()

#############################################################GLOBALS##############################################################
# initLogger() - Initialize the logger object and print some default log text.
#############################################################GLOBALS##############################################################
def initLogger():
    logfile = config.getInstallDir() + "/log/photobooth.log"
    logging.basicConfig(filename=logfile,
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    logging.info("--------------------------------")
    logging.info("------STARTING PHOTOBOOTH-------")
    logging.info("--------------------------------")

#############################################################GLOBALS##############################################################
#
# main() - to initialize configurator and logging
#
def main():
    global config
    config = Configurator.instance()

    initLogger()

    logging.info("sys.path=[%s]" % sys.path)
    global WIDTH
    WIDTH = config.getScreenWidth()

    global HEIGHT
    HEIGHT = config.getScreenHeight()

    # main_win is the root window that takes up the entire screen.
    global main_win
    main_win = Tk() # --> this is the main window
    main_win.attributes("-fullscreen", True)

    # Base thumbnail position
    # Thumbnail characteristics
    global MAX_TN_WIDTH
    MAX_TN_WIDTH = WIDTH / 2

    global MAX_TN_HEIGHT
    MAX_TN_HEIGHT = HEIGHT / 2 - 30

    global MAX_TN_SIZE
    MAX_TN_SIZE = (MAX_TN_WIDTH, MAX_TN_HEIGHT)
    main_win.after_id = None
    main_win.focus_set()

    global frame
    frame = Frame(main_win)
    frame.pack()

    # This is to catch the WM_DELETE_WINDOW arriving when the 'X' is clicked
    # on the main window. We want a clean shutdown, and so we're trapping it.
    main_win.protocol('WM_DELETE_WINDOW', onClose)

    # Create the canvas on which to draw image
    # Register the onClick() handler with the canvas
    global img_display_canvas
    img_display_canvas = Canvas(main_win, width=WIDTH, height=HEIGHT, borderwidth=10, relief="ridge")
    img_display_canvas.pack()
    img_display_canvas.bind('<Button-1>', onClick)  # Register handler for any click (or touch if touchscreen)

    if config.showExitConfigureBtns():
        exit_btn = Button(frame, text="Exit", command=onClose)
        exit_btn.grid(row=1, column=0)
        customize_btn = Button(frame, text="Configure", command=lambda *args: configure(main_win))
        customize_btn.grid(row=1, column=1)

    main_win.bind('q', onClose)

    # Display the default screen - "Click!"
    splashText()

    global is_booth_in_progress
    is_booth_in_progress = False

    # The main windows loop
    main_win.wm_title("VKFamily Photobooth")
    main_win.mainloop()


if __name__ == '__main__':
    main()

##################################################################################################################################
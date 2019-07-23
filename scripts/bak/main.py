
#Imports
import time
import tkMessageBox
import logging
import PIL

from PIL            import ImageTk
from Tkinter        import *
from camera         import *
from util           import *
from camconfig      import *

from upload import uploadImages
from upload import cleanupUploaders

config=Configurator.instance() 
WIDTH 	= config.getScreenWidth()
HEIGHT  = config.getScreenHeight()

#
# main() - to initialize configurator and logging
#
def main():
    logfile = config.getInstallDir() + "/log/photobooth.log"
    logging.basicConfig( filename=logfile, 
                         level=logging.INFO,
                         format='%(asctime)s %(levelname)s %(message)s')
                         
    logging.info("--------------------------------")
    logging.info("------STARTING PHOTOBOOTH-------")
    logging.info("--------------------------------")

if __name__  == '__main__':
    main()
    
# This is a simple GUI, so we allow the main_win singleton to do the legwork
main_win = Tk()
main_win.attributes("-fullscreen",True)

#Base thumbnail position
BASE_TN_X_COORD=120
BASE_TN_Y_COORD=10
IMG_BORDER_PIXELS = 5

# Thumbnail characteristics
MAX_TN_WIDTH  = WIDTH/2
MAX_TN_HEIGHT = HEIGHT/2-30
MAX_TN_SIZE   = (MAX_TN_WIDTH, MAX_TN_HEIGHT)

##################################################################################################################################
# name: displayImage(imgfile, i)
# Displays a thumbnail of the incoming image onto a (grid location) specified by
# the parameter 'i'
##################################################################################################################################
img_to_disp_array=[]
def displayImage(imgfile, i):
       
    logging.info("In displayImage():...")
    
    img = PIL.Image.open(imgfile)
   
    #Create thumbnail of incoming image...
    img.thumbnail(MAX_TN_SIZE, PIL.Image.ANTIALIAS)
    
    #Calculate coordinates of where to display thumbnail
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

CANVAS_TEXT_FONT = ("Helvetica", 50)


##################################################################################################################################
# name: startCountdown()
# Needs the incoming camera argument to start the whole preview process.
# Displays the countdown text one letter at a time (using the CountdownText
# utility class. Stops preview once countdown is completed.
##################################################################################################################################
def startCountdown(camera, canvas, countdown_text="Smile!"):

    camera.start_preview()
    clearCanvas(canvas, "all")
 
    logging.info("Calling CountdownText()...")
    
    CountdownText(text=countdown_text,
                  font=CANVAS_TEXT_FONT,
                  canvas=canvas,
                  fill="purple",
                  x=WIDTH/2, 
                  y=HEIGHT/2+155,
                  anchor=Tkinter.CENTER)        
                  
    logging.info("Back from CountdownText()")
    clearCanvas(canvas, "text")
    camera.stop_preview()

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
picsarray=[]
def startBooth():
    
    logging.info("In startBooth()...")

    num_pics  = config.getNumPics()
    if num_pics > 4: #capping off the number of pictures (within a selfie) to 4 irrespective of configuration
        num_pics = 4
    i=0

    global picsarray
    picsarray=[] #reset
    camera=getCamera()
    clearCanvas(img_display_canvas)
    
    try:    
        # Capture the pics first. 
        # For each pic...
        while i < num_pics:
        
            #...get ready for (next) picture in the session...
            BlinkingText(text="Get ready!",
                            font=CANVAS_TEXT_FONT,
                            fill="purple",
                            blink_freq=.5,
                            num_blinks=3,
                            canvas=img_display_canvas,
                            x=WIDTH/2, y=HEIGHT/2,
                            anchor=Tkinter.CENTER)

        
            #...count it down and...
            startCountdown(camera, img_display_canvas, countdown_text=config.getCountdownText())

            #...snap the picture. Add it to the list of images.
            picsarray.append( camera.snap() )
            if picsarray[i] is None:
                messageBox("Error", "Error", "No pictures were taken!")
                break
            clearCanvas(img_display_canvas);
            i=i+1
            ## End while
        
        # ...then display and upload.
        clearCanvas(img_display_canvas, "all");       
        
        displayImages(picsarray)

        uploadImages(picsarray)
        time.sleep(5) # Arbitrary time to allow people to view thumbnail(s)

        clearCanvas(img_display_canvas, "all");       
        logging.info("Exiting startBooth()")
        
    except Exception as e:
        printExceptionTrace("In startBooth()!", e)
        
    finally:
        camera.close()
        splashText()


##################################################################################################################################
# onClose() - Called in response to the Exit button
##################################################################################################################################
main_win.after_id = None
def onClose(*args, **kw):
    if main_win.after_id is not None:
       main_win.after_cancel(main_win.after_id)
    logging.info("onClose(): Cleaning up uploaders...")
    cleanupUploaders()
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


frame = Frame(main_win)

if config.showExitConfigureBtns():
    exit_btn=Button(frame, text="Exit", command=onClose)
    exit_btn.grid(row=1, column=0)
    customize_btn=Button(frame, text="Configure", command=lambda *args: configure(main_win))
    customize_btn.grid(row=1, column=1)

frame.pack()

# This is to catch the WM_DELETE_WINDOW arriving when the 'X' is clicked
# on the main window. We want a clean shutdown, and so we're trapping it.
main_win.protocol('WM_DELETE_WINDOW', onClose)

##################################################################################################################################
# onClick()
# This method is called in response to a mouse click or a touch on the
# touch screen.
##################################################################################################################################

def onClick(*args):
    startBooth()
    
##################################################################################################################################

# Create the canvas on which to draw image
# Register the onClick() handler with the canvas
img_display_canvas = Canvas(main_win, width=WIDTH, height=HEIGHT, borderwidth=10, relief="ridge")
img_display_canvas.pack()
img_display_canvas.bind('<Button-1>', onClick) #Register handler for any click (or touch if touchscreen)

def splashText():    
    img_display_canvas.config(background="orange")
    img_display_canvas.create_text(WIDTH/2, HEIGHT/2 , text="Touch/Click here to snap!", fill="purple", font=CANVAS_TEXT_FONT, tags="text")
    
splashText()

#The main windows loop
main_win.wm_title("VKFamily Photobooth")
main_win.mainloop()


    
##################################################################################################################################
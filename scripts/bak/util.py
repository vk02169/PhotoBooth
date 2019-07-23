from subprocess import call
from camconfig  import Configurator
from datetime   import datetime

import ConfigParser
import calendar
import time
import tkMessageBox
import sys, traceback
import os
import logging
import Tkinter

class CountdownText(object):
    
    def __init__(self, text, font, fill, canvas, x, y, anchor=Tkinter.CENTER):
        self.text=text
        self.font=font
        self.x=x
        self.y=y
        self.anchor=anchor
        self.canvas=canvas
        self.fill = fill
        self.show(self.fill)
        
    def show(self, fill):
        i=0
        while(i < 1+len(self.text)):
            self.canvas.create_text(self.x, self.y, fill=self.fill, text=self.text[0:i], font=self.font, anchor=self.anchor, tags="text")
            self.canvas.update()
            time.sleep(1)
            clearCanvas(self.canvas, "text")
            i=i+1

class BlinkingText(object):
        
    def __init__(self, text, font, fill, blink_freq, num_blinks, canvas, x, y, anchor=Tkinter.CENTER):
        self.text=text
        self.font=font
        self.x=x
        self.y=y
        self.anchor=anchor
        self.canvas=canvas
        self.count=0
        self.fill=fill
        self.blink_freq=blink_freq
        self.num_blinks=num_blinks
        self.show(self.fill)
   
    def show(self, fill):
        self.canvas.create_text(self.x, self.y, fill=fill, text=self.text, font=self.font, anchor=self.anchor, tags="text")
        self.canvas.update()
        time.sleep(self.blink_freq)
        self.count +=1
        if(self.count < self.num_blinks-3):
            self.hide(fill)
        elif(self.count < self.num_blinks):
            self.show(fill)
        
    def hide(self, fill):
        clearCanvas(self.canvas)
        time.sleep(self.blink_freq)
        self.show(fill)
    
#  
#  name: printExceptionTrace - Prints out an exception trace.
#  @param
#  @return
#  
def printExceptionTrace(message, e):
    print "!!EXCEPTION!! " + message
    line = "-------------------------------------------------"
    print line
    if e is not None:
        print type(e)
        print e.args
        print e
    print line
    logging.error("!!EXCEPTION!! " + message)
    logging.error(line)
    if e is not None:
        logging.error(type(e))
        logging.error(e.args)
        logging.error(str(e))
    logging.error(line)
    ex_type, ex, tb = sys.exc_info()
    extract = traceback.extract_tb(tb)
    logging.error(extract)
    traceback.print_tb(tb)
    del tb

#
# class UniqueIndex - Generates a unique ID 
#
class UniqueIndex(object):
    __instance = None
    
    @staticmethod
    def instance():
        if UniqueIndex.__instance == None:
            UniqueIndex()
        return UniqueIndex.__instance
        
    def __init__(self):
        if UniqueIndex.__instance != None:
            raise Exception ("This is a Singleton object!")
        else:
            UniqueIndex.__instance = self
            
    def getNextIndex(self):
        return calendar.timegm(time.gmtime()) % ( Configurator.instance().getModuloBaseline() )
     

#  
#  name: archiveImage - Archives the incoming image into the archive directory after appending a unique suffix
#  @param
#  @return
#  
def archiveImage (image_filename):

    logging.info("In archiveImage()...")

    config = Configurator.instance()
    archive_dir = config.getArchiveFolder()
    ext = config.getBaseImageExt()
   
   
    next_idx = UniqueIndex.instance().getNextIndex()
    
    logging.info("archive_dir: "    + archive_dir)
    logging.info("image_filename.ext: " + image_filename)
    logging.info("next_idx: " + str(next_idx))

    if os.path.exists(archive_dir) and os.path.exists(image_filename):
        new_filename = os.path.join(archive_dir, '%s_%s.%s' % (image_filename[:-4], str(next_idx), ext))
        logging.info("new_filename: " + new_filename)
        command = (['cp', image_filename, new_filename])
        call(command)
        
    logging.info("In archiveImage(): Exiting...")
    return new_filename

#############################################################################
# messageBox() - For debugging
#############################################################################

def messageBox(state, title, message):
    tkMessageBox.showinfo(title, message)
#############################################################################



#############################################################################
# clearCanvas() - clear items from a canvas. Each item is identified by
# its tag. By default the tag is "all" - everything on the canvas is cleared
#############################################################################

def clearCanvas(canvas, tag="all"):
	canvas.delete(tag)
	canvas.update()
	
#############################################################################


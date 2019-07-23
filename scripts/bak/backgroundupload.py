import threading
import logging

##################################################################################################################################
# Class: BackgroundUploader
# Abstract class that implements background processing. Derived classes need implement only the doUpload() and prepUpload() methods.
# The class implements the standard wait-notify pattern using condition variables.
# Also supports graceful shutdowns (within the cleanup() method.
##################################################################################################################################
class BackgroundUploader(object):

    def __init__(self):
        super(BackgroundUploader, self).__init__()
        self.data_queue = [] # A queue of an array of strings
        self.terminate_flag = False
        self.cv = threading.Condition()
        self.thr = threading.Thread(group=None, name="Uploader", target=self.run, args=(self.cv,))
        self.thr.start()
        self.params_dict={}

    def cleanup(self):
        self.terminate_flag=True
        dummy=["dummy"]
        self.enqueue(self.cv, dummy)

    def doUpload(self, data_array):
        raise NotImplementedError()

    def prepUpload(self, data_array):
        raise NotImplementedError()

    ##################################################################################################################################
    # name - run()
    # This is the standard thread.run() method.
    #   - Blocks on the condition variable cv.
    #   - Once notified (by another thread), queries the data_queue for items to process.
    #   - Looks for a special item called "dummy", which is a signal to terminate the thread.
    #   - Invokes the doUpload() method, implemented by derived classes to do the actual processing.
    #   - Once the data_queue is all empty, goes back to blocking on the condition variable.
    ##################################################################################################################################
    def run(self, cv):
        while True:
            with cv:
                logging.info("BackgroundUploader.run(): Awake now. Number of data sets in 'data_queue' = [%d]" % (
                    len(self.data_queue)))

                if len(self.data_queue) > 0:
                    i = 0
                    while i < len(self.data_queue):
                        data_array = self.data_queue[i]
                        if data_array[0] == "dummy":
                            logging.info("Terminating thread...")
                            return
                        self.doUpload(data_array)
                        i = i + 1
                    self.data_queue = []  # Reset once queue has been drained
                else:
                    logging.info("Nothing to upload; going to get some zzzzs")
                    cv.wait()

    ##################################################################################################################################
    # name - enqueue()
    # This method will be called from a thread that is different from the one that invokes the 'run()' method.
    # enqueue() will be called by producers to push data into the queue for asynchronous processing.
    ##################################################################################################################################
    def enqueue(self, cv, data_array):
        with cv:
            self.data_queue.append(data_array)
            logging.info("BackgroundUploader.enqueue(): Number of data sets in 'data_queue' = [%d]" % (len(self.data_queue)))
            cv.notifyAll() # Wake up threads that are blocking on this condition variable

    ##################################################################################################################################

    ##################################################################################################################################
    # name - upload()
    # Called by producer clients to upload objects.
    # Invokes the enqueue() method
    ##################################################################################################################################
    def upload(self, data_array):
        logging.info( "In BackgroundUploader.upload()")

        #Call the derived class method to give the derived class an opportunity to
        #setup for the real upload.
        if not self.prepUpload(data_array):
            logging.info("In BackgroundUploader.upload() - preUpload() returned false.")
            return False

        #Enqueue the incoming data item for background processing
        self.enqueue(self.cv, data_array)

        logging.info( "In BackgroundUploader.upload() - Exiting.")

    ##################################################################################################################################

    ##################################################################################################################################
    # name - addParam(), getParam()
    # Set name-value parameter pairs to pass arguments to implementing classes
    ##################################################################################################################################
    def addParam(self, name, value):
        self.params_dict[name]=value

    def getParam(self, name):
        return self.params_dict[name]

    ##################################################################################################################################



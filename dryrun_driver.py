#!/usr/bin/python

'''dryrun_driver.py: 
This code is the driver script for dryrun.py, documented seperately.
Basically what this script does is sets the IMAP server in IDLE mode so
as to be notified when a new email arrives. However before doing that,
it first invokes dryrun_invoke() to check for any existing unprocessed
requests.

Built upon
http://blog.timstoop.nl/2009/03/11/python-imap-idle-with-imaplib2/

Amit Saha < droidery@gmail.com> 
http://echorand.me
Version PoC: 27 August, 2011
'''


# uses impalib2: https://www.it.usyd.edu.au/~piers/python/imaplib2

import imaplib2, time
from threading import *

import logging

from dryrun import *

# Global configs for the mailbox which acts
# as the receiever for code execution requestions
IMAP_SERVER = 'imap.gmail.com'
username = 'your username'
password = 'your password'

# This is the threading object that does all the waiting on 
# the event
class Idler(object):
    def __init__(self, conn):
        self.thread = Thread(target=self.idle)
        self.M = conn
        self.event = Event()
        
    def start(self):
        self.thread.start()
        
    def stop(self):
        # This is a neat trick to make thread end. Took me a 
        # while to figure that one out!
        self.event.set()
        
    def join(self):
        self.thread.join()
        
    def idle(self):
        # Starting an unending loop here
        while True:
            # This is part of the trick to make the loop stop 
            # when the stop() command is given
            if self.event.isSet():
                return
            self.needsync = False
            # A callback method that gets called when a new 
            # email arrives. Very basic, but that's good.
            def callback(args):
                if not self.event.isSet():
                    self.needsync = True
                    self.event.set()
            # Do the actual idle call. This returns immediately, 
            # since it's asynchronous.
            self.M.idle(callback=callback)
            # This waits until the event is set. The event is 
            # set by the callback, when the server 'answers' 
            # the idle call and the callback function gets 
            # called.
            self.event.wait()
            # Because the function sets the needsync variable,
            # this helps escape the loop without doing 
            # anything if the stop() is called. Kinda neat 
            # solution.
            if self.needsync:
                self.event.clear()
                self.dosync()
                
    # The method that gets called when a new email arrives. 
    # Replace it with something better.
    def dosync(self):

        logging.info('Got a request for processing..')
        # invoke dryrun
        dryrun_invoke()

# Register a IDLE for the mailbox
if __name__=='__main__':
    
    # Init. logger
    logging.basicConfig(filename='dryrun.log',level=logging.DEBUG,format='%(asctime)s %(message)s')
    logging.info('Starting Dryrun...')

    # Check for any unattended new requests
    dryrun_invoke()


    # Register IDLE mode with the IMAP server and 
    # wait
    M = imaplib2.IMAP4_SSL(IMAP_SERVER)
    M.login(username,password)
    # We need to get out of the AUTH state, so we just select 
    # the INBOX.
    M.select("INBOX")
    # Start the Idler thread
    idler = Idler(M)
    idler.start()
    
    #keep alive for ever
    while 1:
        time.sleep(1*360)

    # Clean up.
    idler.stop()
    idler.join()
    M.close()
    # This is important!
    M.logout()

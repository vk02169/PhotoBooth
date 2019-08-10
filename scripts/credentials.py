import os
import gdata
import gdata.photos.service
import gdata.media
import gdata.geo
import gdata.gauth
import webbrowser
import httplib2
from datetime import datetime, timedelta
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
import logging

import getpass
import os.path

install_dir = os.path.split(os.path.abspath(__file__))[0]
class Credential:
    def __init__(self):
        self.filename = os.path.join(install_dir, '.credentials')

        if os.path.exists(self.filename):
            f = open(self.filename)
            self.key = f.readline().strip()
            self.value = f.readline().strip()
        else:
            self.key = raw_input('Google Username:')
            self.value = getpass.getpass('App Specific Password')
            f = open(self.filename, 'w')
            f.write(self.key + '\n')
            f.write(self.value + '\n')

cred = Credential()
username = cred.key
password = cred.value
gmailUser = username
gmailPassword = password

def OAuth2Login(client_secrets, credential_store, email):
    scope='https://picasaweb.google.com/data/'
    user_agent='picasawebuploader'

    logging.info("OAuth2Login(): credential store:[%s], email: [%s]"%(credential_store, email))

    storage = Storage(credential_store)
    credentials = storage.get()

    logging.info("OAuth2Login(): Credentials in storage =[%s]"%credentials)

    if credentials is None or credentials.invalid:
        logging.info("OAuth2Login(): No credentials in Storage()...getting authorized via browser")
        flow = flow_from_clientsecrets(client_secrets, scope=scope, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        uri = flow.step1_get_authorize_url()
        logging.info("OAuth2Login(): URI: [%s]"%uri)
        webbrowser.open(uri)

        logging.info("OAuth2Login(): back from webbrowser")

        code = raw_input('Enter the authentication code: ').strip()
        credentials = flow.step2_exchange(code)

    if (credentials.token_expiry - datetime.utcnow()) < timedelta(minutes=5):
        logging.info("OAuth2Login(): Refreshing credentials...")
        http = httplib2.Http()
        http = credentials.authorize(http)
        credentials.refresh(http)

    storage.put(credentials)

    logging.info("OAuth2Login(): Calling gdata.photos.service.PhotosService: source[%s], email: [%s]" % (user_agent, email))
    gd_client = gdata.photos.service.PhotosService(source=user_agent,
                                                   email=email,

                                                   additional_headers={'Authorization' : 'Bearer %s' % credentials.access_token})

    return gd_client

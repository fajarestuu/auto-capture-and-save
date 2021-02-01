from __future__ import print_function
import cv2
from datetime import datetime
import time
import configparser
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

config = configparser.ConfigParser()
# load your configuration file
# template is in config.sample.ini
config.read('config.ini')

SCOPES = [config['PATH']['scopes']]


def takePicture():
    vs = cv2.VideoCapture(0)

    frameCount = 0
    while True:
        ret, frame = vs.read()
        frameCount = frameCount + 1
        if frameCount > 3:
            imgName = str(datetime.now())
            imgName = imgName.replace(':', '-')
            imgName = config['PATH']['image']+imgName+'.png'
            cv2.imwrite(imgName, frame)
            break
        cv2.waitKey(10)

    vs.release()
    return imgName


def main():
    picture = takePicture()

    creds = None

    if os.path.exists(config['PATH']['pickle']):
        with open(config['PATH']['pickle'], 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config['PATH']['clientSecrets'], SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(config['PATH']['pickle'], 'wb') as token:
            pickle.dump(creds, token)

    uploaded = False
    parent = config['DRIVE']['parents']

    while uploaded is False:
        try:
            service = build('drive', 'v3', credentials=creds)
            file_metadata = {'name': picture, 'parents': [parent]}
            media = MediaFileUpload(picture, mimetype='image/png')
            file = service.files().create(body=file_metadata,
                                          media_body=media,
                                          fields='id').execute()
            uploaded = True
        except:
            print('waiting')
            time.sleep(10)
            continue


if __name__ == '__main__':
    main()

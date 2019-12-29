from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors
import csv
from time import time
from time import sleep

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

"""Get a list of Messages from the user's mailbox.
"""

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if (os.path.exists('token.pickle')):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    startTime = time()
    endTime = 'null'
   
    """
    Testing for one loop that breaks when there is 'none' return from listing
    """
    pageToken = 'null'
    resultsPerThread = 500
    count = 0
    with open('emails.tsv', 'w+', newline='', encoding='utf-8') as csvfile:
        csvfile.write('Sender\tSubject\tTimestamp\tSnippet\n')
        while True:
            msgList = 'null'
            idList = 'null'
            if (pageToken == None):
                break
            elif (pageToken == 'null'):
                print ("This thread's token: " + str(pageToken))
                msgList = service.users().messages().list(userId='me', labelIds=['UNREAD'], maxResults=resultsPerThread).execute()
            else:
                print ("This thread's token: " + str(pageToken))
                msgList = service.users().messages().list(userId='me', labelIds=['UNREAD'], maxResults=resultsPerThread, pageToken=pageToken).execute()
            idList = msgList.get('messages') # Breaks the message list down into just the list of 'id' and the actual id
            for idDict in idList:
                count += 1
                print ("Parsing message #" + str(count) + " with messageId: " + idDict['id'])
                tempMsg = service.users().messages().get(userId='me', id=idDict['id'], format='metadata').execute()
                sender = 'null'
                subject = 'null'
                timestamp = 'null'
                snippet = 'null' 
                for rename in tempMsg['payload']['headers']:
                    if (rename['name'] == 'From'):
                        sender = rename['value']
                    elif (rename['name'] == 'Subject'):
                        subject = rename['value']
                timestamp = tempMsg['internalDate']
                snippet = tempMsg['snippet']
                if ('\t' in sender or '\t' in subject or '\t' in snippet):
                    print("RED ALERT")
                csvfile.write(sender + '\t' + subject +  '\t' + timestamp + '\t' + snippet + '\n')
            pageToken = msgList.get('nextPageToken')
    endTime = time()
    timeElapsed = endTime - startTime
    hours = int(timeElapsed / (60 * 60))
    minutes = int((timeElapsed - (hours * 60 * 60) )/ 60)
    seconds = round(timeElapsed % (60), ndigits=2)
    print ("Total Count: " + str(count) + " messages")
    print ("Time Elapsed: " + str(hours) + "h " + str(minutes) + "m " + str(seconds) + "s")
    



    
if __name__ == '__main__':
    main()
    



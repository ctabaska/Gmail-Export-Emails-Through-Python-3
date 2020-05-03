from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors
from time import time
from time import sleep

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

"""Get a list of Messages from the user's mailbox.
"""
def splitString(string): # Takes a string as input and splits it in between the less than and greater sign
    if(len(string.split('<')) > 1):
        return string.split('<')[1].split('>')[0]
    return string
    

def callback(response_id, response, exception):
    print(response)

    sender = 'null'
    subject = 'null'
    recipient = 'null'
    
    if ('labelIds' in response): # Checks if there are 'labelIds'
        if('CHAT' in response.get('labelIds')): # 'Chat' emails get rejected because they don't contain enough information to be useful
            return None
    else:
        return None

    if ('payload' in response and 'headers' in response.get('payload')):
        for header in response.get('payload').get('headers'):
            if (header['name'] == 'To'):
                recipient = splitString(header['value'])
            elif (header['name'] == 'From'):
                sender = splitString(header['value'])
            elif (header['name'] == 'Subject'):
                subject = header['value']
    else:
        print('Error finding \'payload\' in response')
    
    if (sender == 'null'):
        print ('\'From\' header could not be found')

    if (recipient == 'null'):
        print ('\'To\' header could not be found')
    
    if (subject == 'null'):
        print ('\'Subject\' header could not be found')


    print(sender + ' -> ' + recipient + ' - ' + subject)
    with open('emails.tsv', 'a', newline='', encoding='utf-8') as tsvfile:
        tsvfile.write(response.get('id') + '\t' + sender + '\t' + recipient + '\t' + subject + '\n')
    print('\n')



def createBatch(service, callback, id_list): # Creates a batch http request with all the ids recieved and then returns it
    batch = service.new_batch_http_request(callback)
    for id_pair in id_list:
        temp_id = id_pair.get('id')
        batch.add(service.users().messages().get(userId='me', id=temp_id, format='metadata', metadataHeaders=['From', 'Subject', 'To']))
    return batch

def getEmailList(service, numResults, nextPageToken=None): # Gets a list of all the messages in the next stack
    return service.users().messages().list(userId='me', maxResults=numResults, pageToken=nextPageToken).execute()


def main():

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

    nextPageToken = None # Next page token is used to find the next set of messages in the stack of emails
    batchCount = 0

    # Opens 'emails.tsv' and creates a header
    with open('emails.tsv', 'w+', newline='', encoding='utf-8') as tsvfile:
        tsvfile.write('Message Id\tSender\tRecipient\tSubject\n')
    
    while True:
        batchCount += 1
        msgsList = getEmailList(service, 40, nextPageToken)

        nextPageToken = msgsList.get('nextPageToken')

        id_list = msgsList.get('messages')

        batch = createBatch(service, callback, id_list)
        
        batch.execute()
        print('Batch number: ' + str(batchCount))
        if(nextPageToken == None):
            break
    
    emailCount = {}
    count = 0

    # Loops through 'emails.tsv' to check frequency of who you got emails from
    with open('emails.tsv', 'r') as emailList:
        while True:
            test = emailList.readline()
            if (test == ''): # Check if eof
                break
            test = test.split('\t')[1]

            if (test not in emailCount): 
                count += 1
                emailCount[test] = 1
            else:
                emailCount[test] += 1

    with open('email_frequency.tsv', 'w+', newline='', encoding='utf-8') as tsvfile:
        for keyValue in emailCount:
            tsvfile.write(keyValue + '\t' + str(emailCount.get(keyValue)) + '\n')


    
if __name__ == '__main__':
    main()
    



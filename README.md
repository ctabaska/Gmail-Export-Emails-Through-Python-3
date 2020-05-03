# Gmail-Sender-Frequency-Exporter-Python-3
Creates a tsv file of emails and frequency of senders

## How to set it up
1. Install Python 3.6 or newer
2. Follow the instructions to enable the api on the [Gmail api website](https://developers.google.com/gmail/api/quickstart/python).
3. Download the client configuration as `crendentials.json` and move it to the same folder as `quickstart.py`.
4. Install the Google Client Library using the pip managment tool in command line: `pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`.
5. Run `python quickstary.py`, it will ask you to authorize use of your gmail account.

## What it does
This programs runs through every email in your inbox and creates `emails.tsv` in the format: message id, sender, recipient, and subject.
It then takes that spreadsheet and checks how many times each sender sent an email to your inbox and writes it to `email_frequency.tsv`.

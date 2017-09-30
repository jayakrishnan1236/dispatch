#!flask/bin/python
from flask import Flask, request, abort
import boto3
import config

class Email(object):  
    
    def __init__(self, to, subject):
        self.to = to
        self.subject = subject
        self._html = None
        self._text = None
        self._format = 'html'

    def html(self, html):
        self._html = html

    def text(self, text):
        self._text = text

    def send(self, from_addr=None):
        body = self._html

#        if isinstance(self.to, basestring):
#            self.to = [self.to]
        if not from_addr:
            from_addr = 'noreply@sensehawk.com'
        if not self._html and not self._text:
            raise Exception('You must provide a text or html body.')
        if not self._html:
            self._format = 'text'
            body = self._text

        connection = boto3.client(
            'ses',
            config.PRIMARY_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY, 
            aws_secret_access_key=config.AWS_SECRET_KEY
        )


        return connection.send_email(
            Destination={
                'ToAddresses': self.to
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': self._html,
                    },
                    'Text': {
                        'Charset': 'UTF-8',
                        'Data': self._text,
                    },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': self.subject
                },
            },
            Source= from_addr
        )


# FLASK part
app = Flask(__name__)

@app.route('/send', methods=['POST'])
def send_email_flask():
    if not request.json or not 'subject' in request.json:
        abort(400)

    data = request.get_json()

    TO_EMAIL = str(data['to_email'].encode('utf8'))
    TO_EMAILS = TO_EMAIL.split(",")
    SUBJECT = data['subject']
    EMAIL_HTML = data['html']
    EMAIL_RAW = data['raw']

    # Sending the actual email
    email = Email(to=TO_EMAILS, subject=SUBJECT)  
    email.text(EMAIL_RAW)  
    email.html(EMAIL_HTML)  # Optional  
    email.send()
    
    return "<h1>Email sent with subject "+request.json['subject']+"!</h1>", 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)



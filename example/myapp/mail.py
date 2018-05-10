# myapp/mail.py

def send_email(address, body, title=None):
    email = {
        'address': address,
        'body': body,
        'title': title or 'Cool email'
    }
    print '\n#### Sending email: %s ####\n' % email

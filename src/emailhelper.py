import smtplib
import confighelper
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class email_client:
    def __init__(self):
        config = confighelper.read_config()

        self.smtp_server = config['EmailSettings']['smtp_server']
        self.smtp_port = config.getint('EmailSettings','smtp_port')
        self.username = config['EmailSettings']['username']
        self.password = config['EmailSettings']['password']
        self.recipient = config['EmailSettings']['recipient']

    def sendmail(self, recipient, subject, content, image):

        # add headers
        headers = ["From: " + self.username, "Subject: " + subject, "To: " + recipient,
                   "MIME-Version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers)

        # add general email info
        msg = MIMEMultipart('alternative')
        msg['From'] = self.username
        msg['To'] = recipient
        msg['Subject'] = subject

        # attach image to email
        img = MIMEImage(image, 'jpg')
        img.add_header('Content-ID', 'image')
        msg.attach(img)

        # embed image in email
        text = f"{content}<img src='cid:image'>"
        bodytext = MIMEText(text, 'html')
        msg.attach(bodytext)

        # connect to server
        session = smtplib.SMTP(self.smtp_server, self.smtp_port)
        session.ehlo()
        session.starttls()
        session.ehlo()

        # login to gmail
        session.login(self.username, self.password)

        # send email 
        session.sendmail(self.username, recipient, msg.as_string())

        # quit session
        session.quit
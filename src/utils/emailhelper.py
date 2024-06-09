import smtplib
import confighelper
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import matplotlib.pyplot as plt
from matplotlib import rcParams
import io

class email_client:
    def __init__(self):
        config = confighelper.read_config()

        self.smtp_server = config['EmailSettings']['smtp_server']
        self.smtp_port = config.getint('EmailSettings','smtp_port')
        self.username = config['EmailSettings']['username']
        self.password = config['EmailSettings']['password']
        self.recipient = config['EmailSettings']['recipient']

    def sendmail(self, recipient, subject, content, images):

        # add headers
        headers = ["From: " + self.username, "Subject: " + subject, "To: " + recipient,
                   "MIME-Version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers)

        # add general email info
        msg = MIMEMultipart('related')
        msg['From'] = self.username
        msg['To'] = recipient
        msg['Subject'] = subject

        # Define the HTML content of the email
        html = """
        <html>
        <body>
        """
        html = html + f"<p>{content}</p>"

        for index, image in enumerate(images):
            # embed image in email
            text = f"<p><img src='cid:image{index}'></p>"
            # bodytext = MIMEText(text, 'html')
            # msg.attach(bodytext)
            html = html + text

        html = html + """
        </body>
        </html>
        """
        bodytext = MIMEText(html, 'html')
        msg.attach(bodytext)

        for index, image in enumerate(images):
            # attach image to email
            img = MIMEImage(image, 'jpg')
            img.add_header('Content-ID', f'image{index}')
            img.add_header('Content-Disposition','inline', filename=f'image{index}')
            
            msg.attach(img)

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

class email_helper:      

    def df_to_plot_table (self, df):
        fig, ax = plt.subplots()
  
        # hide axes
        fig.patch.set_visible(False)
        ax.axis('off')
        ax.axis('tight')
        table = ax.table(cellText=df.values, colLabels=df.columns,  loc='center')
        fig.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='jpg')
        buf.seek(0)
        data = buf.read()

        return data
        
    def df_to_plot_bar(self, df):
        rcParams.update({'figure.autolayout': True})
        df.sort_values(by='margin', ascending=True).plot(kind='bar', y=['margin'], x='ticker')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='jpg')
        buf.seek(0)
        data = buf.read()

        return data        
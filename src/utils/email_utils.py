import smtplib
from src.utils.config_utils import read_email_config, EmailConfig
from src.utils.references import EMAIL_CONFIG
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import dataframe_image as dfi
from PIL import Image

import matplotlib.pyplot as plt
from matplotlib import rcParams
import io

class email_client:
    def __init__(self):
        config = read_email_config(EMAIL_CONFIG)

        self.smtp_server = config.smtp_server
        self.smtp_port = config.smtp_port
        self.username = config.username
        self.password = config.password
        self.recipient = config.recipient

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

    def df_to_plot_table(self, df, debug=False):
        # Increase the figure size
        fig, ax = plt.subplots(figsize=(12, 8))
        buf = io.BytesIO()

        dfi.export(df, buf, table_conversion='matplotlib')
        buf.seek(0)
        if debug:
            image = Image.open(buf)
            image.show()
        data = buf.read()

        return data
        
    def df_to_plot_bar(self, df, debug=False):
        rcParams.update({'figure.autolayout': True})

        # Sort the DataFrame by 'margin'
        df_sorted = df.sort_values(by='margin', ascending=True)

        # Determine colors based on 'action' column
        colors = df_sorted['action'].map({'buy': 'green', 'sell': 'orange', 'hold': 'gray'})

        # Create a bar plot
        fig, ax = plt.subplots()
        bars = ax.bar(df_sorted['ticker'], df_sorted['margin'], color=colors)

        # Apply hatches to bars where execute is False
        for bar, execute in zip(bars, df_sorted['execute']):
            if not execute:
                bar.set_hatch('/')

        # Annotate the cooldown values above the bars
        for bar, cooldown in zip(bars, df_sorted['cooldown']):
            height = bar.get_height()
            ax.annotate(f'{cooldown}', 
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')                

        # Set labels and title
        ax.set_xlabel('Ticker')
        ax.set_ylabel('Margin')
        ax.set_title('Ticker by Margin')

        # Rotate x-axis labels vertically
        plt.xticks(rotation=90)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='jpg')
        buf.seek(0)
        if debug:
            image = Image.open(buf)
            image.show()
        data = buf.read()

        return data        
from data_processing.pdf.data_processing import PageController
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailController:
    
    def __init__(self):
        self.ai = PageController()

    def send_error_email(self, subject, body):
        ops_mail = self.ai.ops_mail()
        ops_mail_password = self.ai.ops_mail_password()

        sender_email   = ops_mail
        # receiver_email = ops_mail
        receiver_email = 'allyson.bueno@involves.com'
        password       = ops_mail_password

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Error email sent successfully.")
            server.quit()
        except Exception as e:
            print(f"Failed to send error email: {e}")
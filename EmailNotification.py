import smtplib
import datetime
import logging

logging.basicConfig(level=logging.INFO)

class email_notification:
    def __init__(self):
        self.sender = ''
        self.password = ''
        self.admin = ''

    def sendEmail(self, name, email,timestamp, type, place):
        timestamp = timestamp.strftime("%m/%d/%Y, %H:%M:%S")
        if type == 'Mask':
            message = 'Subject: {}\n\n{}'.format('SOP Violation Notification', '''Dear ''' + name + '''

    You have been observed violating the SOPs at ''' + timestamp + '''. 

    For the safety of your coworkers, please ensure that all SOPs are being followed.''')
            session =  smtplib.SMTP('smtp.gmail.com', 587)
            session.starttls()
            session.login(self.sender,self.password)
            session.sendmail(self.sender, email, message)
            session.quit()

            logging.info('Successfully sent email to violator')
            
            
        if type == 'Crowd':
            message = 'Subject: {}\n\n{}'.format('Crowd Detected', '''A Crowd has been detected on ''' + timestamp + '''. 

    at ''' + place + '''. Please send authorities to disperse crowd.''')
            session =  smtplib.SMTP('smtp.gmail.com', 587)
            session.starttls()
            session.login(self.sender,self.password)
            session.sendmail(self.sender, self.admin, message)
            
            session.quit()
            
            logging.info('Successfully sent email to admin')

